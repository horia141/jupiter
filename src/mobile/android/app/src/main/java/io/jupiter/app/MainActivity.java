package io.jupiter.app;

import android.net.Uri;
import android.os.Bundle;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebView;
import com.getcapacitor.Bridge;
import com.getcapacitor.BridgeActivity;
import com.getcapacitor.BridgeWebViewClient;

public class MainActivity extends BridgeActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        bridge.setWebViewClient(new ShellWebViewClient(bridge));
    }

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
