import 'package:flet/flet.dart';
import 'media_scanner_service.dart';

class Extension extends FletExtension {
  @override
  void ensureInitialized() {}

  @override
  FletService? createService(Control control) {
    switch (control.type) {
      case "MediaScanner":
        return MediaScannerService(control: control);
      default:
        return null;
    }
  }
}
