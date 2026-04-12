import 'package:flutter/material.dart';

class AppColors {
  AppColors._();
  
  // Primary colors
  static const Color background = Color(0xFF0D0D0D);
  static const Color surface = Color(0xFF1E1E2E);
  static const Color surfaceLight = Color(0xFF2A2A3E);
  
  // Brand colors
  static const Color primary = Color(0xFF6C5CE7);
  static const Color secondary = Color(0xFFA29BFE);
  static const Color accent = Color(0xFFFD79A5);
  static const Color premium = Color(0xFFF9CA24);
  
  // Text colors
  static const Color textPrimary = Color(0xFFFFFFFF);
  static const Color textSecondary = Color(0xFFB2B2B2);
  static const Color textMuted = Color(0xFF666666);
  
  // Status colors
  static const Color success = Color(0xFF00D9A5);
  static const Color error = Color(0xFFFF6B6B);
  static const Color warning = Color(0xFFF9CA24);
  
  // Gradients
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [primary, secondary],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  static const LinearGradient darkGradient = LinearGradient(
    colors: [background, surface],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );
}
