import 'dart:convert';

import 'package:flet/flet.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:media_scanner/media_scanner.dart';

class MediaScannerService extends FletService {
  static const MethodChannel _channel =
      MethodChannel('flet_media_scanner/scan');

  MediaScannerService({required super.control});

  @override
  void init() {
    super.init();
    control.addInvokeMethodListener(_onInvokeMethod);
    debugPrint("MediaScannerService: initialized");
  }

  Future<dynamic> _onInvokeMethod(String methodName, dynamic args) async {
    Map<String, dynamic> arguments = {};
    if (args != null && args is Map) {
      arguments = Map<String, dynamic>.from(args);
    }

    debugPrint(
        "MediaScannerService._onInvokeMethod: $methodName args=$arguments");

    return switch (methodName) {
      "save_video" => await _saveVideo(arguments),
      "scan_media" => await _scanMedia(arguments),
      _ => throw Exception("MediaScannerService: unknown method '$methodName'"),
    };
  }

  Future<String> _saveVideo(Map<String, dynamic> args) async {
    final String? path = args["path"] as String?;
    final String? fileName = args["file_name"] as String?;
    final String album = args["album"] as String? ?? "Vidsaver";
    if (path == null || path.isEmpty) {
      return _encodeResult({
        "success": false,
        "error": "path is required",
      });
    }

    try {
      final result = await _channel.invokeMethod<Map<dynamic, dynamic>>(
        'saveVideo',
        {
          'path': path,
          'fileName': fileName,
          'album': album,
        },
      );
      final payload = Map<String, dynamic>.from(result ?? {});
      control.triggerEvent("saved", payload);
      return _encodeResult(payload);
    } on PlatformException catch (e) {
      final payload = {
        "success": false,
        "path": path,
        "error": "${e.code}: ${e.message}",
      };
      control.triggerEvent("saved", payload);
      return _encodeResult(payload);
    } catch (error, stack) {
      debugPrint("MediaScannerService._saveVideo: ERROR '$path': $error\n$stack");
      final payload = {
        "success": false,
        "path": path,
        "error": error.toString(),
      };
      control.triggerEvent("saved", payload);
      return _encodeResult(payload);
    }
  }

  Future<String> _scanMedia(Map<String, dynamic> args) async {
    final String? path = args["path"] as String?;
    if (path == null || path.isEmpty) {
      debugPrint("MediaScannerService._scanMedia: path is null or empty");
      control.triggerEvent(
          "scanned", {"path": path ?? "", "success": "false", "error": "path is required"});
      return "false";
    }

    debugPrint("MediaScannerService._scanMedia: scanning '$path'");

    try {
      await MediaScanner.loadMedia(path: path);
      debugPrint(
          "MediaScannerService._scanMedia: media_scanner completed path='$path'");
      control.triggerEvent("scanned", {
        "path": path,
        "success": "true",
        "result": "scanned",
      });
      return "true";
    } catch (error, stack) {
      debugPrint(
          "MediaScannerService._scanMedia: ERROR '$path': $error\n$stack");
      control.triggerEvent("scanned", {
        "path": path,
        "success": "false",
        "error": error.toString(),
      });
      return "false";
    }
  }

  String _encodeResult(Map<String, dynamic> payload) {
    return jsonEncode(payload);
  }

  @override
  void dispose() {
    debugPrint("MediaScannerService: disposed");
    super.dispose();
  }
}
