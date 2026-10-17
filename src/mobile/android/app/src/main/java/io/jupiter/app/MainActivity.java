package io.jupiter.app;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.util.Log;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebView;
import com.getcapacitor.Bridge;
import com.getcapacitor.BridgeActivity;
import com.getcapacitor.BridgeWebViewClient;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginHandle;
import java.lang.reflect.Method;
import java.util.Collections;
import androidx.webkit.WebViewCompat;
import androidx.webkit.WebViewFeature;
import ee.forgr.capacitor.social.login.GoogleProvider;
import ee.forgr.capacitor.social.login.ModifiedMainActivityForSocialLoginPlugin;
import ee.forgr.capacitor.social.login.SocialLoginPlugin;

public class MainActivity extends BridgeActivity implements ModifiedMainActivityForSocialLoginPlugin {

    private static final String LOG_TAG = "MainActivity";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        bridge.setWebViewClient(new ShellWebViewClient(bridge));
        injectBridgeIntoAnyServer();
    }

    /**
     * Capacitor only injects its bridge (the plugin list and the JS API) into pages of the app's own origin. The shell
     * loads the webui from whatever server the user picked, so without this none of the plugins work in the webui: the
     * platform reads as android, but every plugin call fails with "not implemented". The shell already lets the
     * webview go anywhere ({@code allowNavigation: ["*"]}), so the bridge goes wherever it does.
     *
     * Capacitor keeps the script behind a private method, so it takes reflection to get at it.
     */
    private void injectBridgeIntoAnyServer() {
        if (!WebViewFeature.isFeatureSupported(WebViewFeature.DOCUMENT_START_SCRIPT)) {
            Log.w(LOG_TAG, "The webview can't run scripts at document start, so plugins won't work on remote servers");
            return;
        }

        try {
            Method getInjector = Bridge.class.getDeclaredMethod("getJSInjector");
            getInjector.setAccessible(true);
            Object injector = getInjector.invoke(bridge);

            Method getScriptString = injector.getClass().getDeclaredMethod("getScriptString");
            getScriptString.setAccessible(true);
            String script = (String) getScriptString.invoke(injector);

            WebViewCompat.addDocumentStartJavaScript(bridge.getWebView(), script, Collections.singleton("*"));
        } catch (ReflectiveOperationException | RuntimeException ex) {
            Log.e(LOG_TAG, "Could not inject the Capacitor bridge into remote servers", ex);
        }
    }

    /**
     * The social login plugin refuses Google's offline mode (which we use, to get a serverAuthCode for the backend)
     * unless the main activity says it passes on the result of Google's authorisation screen.
     */
    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode < GoogleProvider.REQUEST_AUTHORIZE_GOOGLE_MIN || requestCode >= GoogleProvider.REQUEST_AUTHORIZE_GOOGLE_MAX) {
            return;
        }

        PluginHandle pluginHandle = getBridge().getPlugin("SocialLogin");
        if (pluginHandle == null) {
            Log.i(LOG_TAG, "SocialLogin plugin handle is null");
            return;
        }

        Plugin plugin = pluginHandle.getInstance();
        if (!(plugin instanceof SocialLoginPlugin)) {
            Log.i(LOG_TAG, "SocialLogin plugin instance is not a SocialLoginPlugin");
            return;
        }

        ((SocialLoginPlugin) plugin).handleGoogleLoginIntent(requestCode, data);
    }

    @Override
    public void IHaveModifiedTheMainActivityForTheUseWithSocialLoginPlugin() {}

    /**
     * Capacitor's client, plus one rule of the app shell: a server that answers with a 5xx gets the shell's error
     * page, and the page is told the status. Capacitor shows its error page for any 4xx or 5xx, but a 4xx is a page
     * the webui renders itself (a 404, say), not a broken server.
     */
    private static class ShellWebViewClient extends BridgeWebViewClient {

        private final Bridge bridge;

        ShellWebViewClient(Bridge bridge) {
            super(bridge);
            this.bridge = bridge;
        }

        // Unlike Capacitor's, this doesn't tell WebViewListeners about the error: the list isn't public, and none of
        // the plugins we ship listen for HTTP errors.
        @Override
        public void onReceivedHttpError(WebView view, WebResourceRequest request, WebResourceResponse errorResponse) {
            String errorUrl = bridge.getErrorUrl();
            int status = errorResponse.getStatusCode();
            if (errorUrl == null || !request.isForMainFrame() || status < 500) {
                return;
            }

            view.loadUrl(
                Uri.parse(errorUrl)
                    .buildUpon()
                    .appendQueryParameter("reason", "http")
                    .appendQueryParameter("code", String.valueOf(status))
                    .appendQueryParameter("url", request.getUrl().toString())
                    .build()
                    .toString()
            );
        }
    }
}
