import Capacitor
import UIKit
import WebKit

/// Capacitor's bridge, plus one rule of the app shell: a server that answers
/// with a 5xx gets the shell's error page, just like one that can't be
/// reached. Capacitor itself only shows the error page for the latter.
class ShellViewController: CAPBridgeViewController {
    // The web view only holds its navigation delegate weakly.
    private var navigationDelegate: ShellNavigationDelegate?

    override func capacitorDidLoad() {
        super.capacitorDidLoad()

        guard let webView = webView, let capacitorDelegate = webView.navigationDelegate else {
            return
        }

        let delegate = ShellNavigationDelegate(
            wrapping: capacitorDelegate,
            errorURL: bridge?.config.errorPathURL
        )
        navigationDelegate = delegate
        webView.navigationDelegate = delegate
    }
}

/// Stands in front of Capacitor's navigation delegate, forwarding everything
/// to it except the response check it doesn't do.
final class ShellNavigationDelegate: NSObject, WKNavigationDelegate {
    private let wrapped: WKNavigationDelegate
    private let errorURL: URL?
    // Cancelling a response makes WebKit fail the navigation, which Capacitor
    // would answer by loading its plain error page over ours.
    private var isShowingErrorPage = false

    init(wrapping wrapped: WKNavigationDelegate, errorURL: URL?) {
        self.wrapped = wrapped
        self.errorURL = errorURL
    }

    override func responds(to aSelector: Selector!) -> Bool {
        super.responds(to: aSelector) || wrapped.responds(to: aSelector)
    }

    override func forwardingTarget(for aSelector: Selector!) -> Any? {
        wrapped.responds(to: aSelector) ? wrapped : super.forwardingTarget(for: aSelector)
    }

    func webView(
        _ webView: WKWebView,
        decidePolicyFor navigationResponse: WKNavigationResponse,
        decisionHandler: @escaping (WKNavigationResponsePolicy) -> Void
    ) {
        guard navigationResponse.isForMainFrame,
              let response = navigationResponse.response as? HTTPURLResponse,
              response.statusCode >= 500,
              let errorPage = errorPageURL(status: response.statusCode, url: response.url) else {
            decisionHandler(.allow)
            return
        }

        isShowingErrorPage = true
        decisionHandler(.cancel)
        webView.load(URLRequest(url: errorPage))
    }

    func webView(
        _ webView: WKWebView,
        didFailProvisionalNavigation navigation: WKNavigation!,
        withError error: Error
    ) {
        if isShowingErrorPage {
            isShowingErrorPage = false
            return
        }

        wrapped.webView?(webView, didFailProvisionalNavigation: navigation, withError: error)
    }

    private func errorPageURL(status: Int, url: URL?) -> URL? {
        guard let errorURL = errorURL,
              var components = URLComponents(url: errorURL, resolvingAgainstBaseURL: false) else {
            return nil
        }

        components.queryItems = [
            URLQueryItem(name: "reason", value: "http"),
            URLQueryItem(name: "code", value: String(status)),
            URLQueryItem(name: "url", value: url?.absoluteString ?? "")
        ]
        return components.url
    }
}
