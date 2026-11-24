import SwiftUI

struct InvoiceExport: View {
    let invoice: Data
    let destination: URL
    @State private var message: String?

    var body: some View {
        Button(action: save) {
            Image(systemName: "square.and.arrow.up")
                .accessibilityLabel(Text("invoice.export.button"))
        }
        if let message {
            Text(message)
        }
    }

    private func save() {
        do {
            try invoice.write(to: destination)
            message = nil
        } catch {
            let messageFormat = NSLocalizedString("invoice.export.failed", comment: "Shown after a file write fails")
            message = String(format: messageFormat, destination.lastPathComponent)
        }
    }
}
