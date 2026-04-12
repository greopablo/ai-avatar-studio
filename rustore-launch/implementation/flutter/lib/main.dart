import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/home_screen.dart';
import 'screens/generation_screen.dart';
import 'screens/results_screen.dart';
import 'services/api_service.dart';
import 'models/user.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => UserProvider()),
        Provider(create: (_) => ApiService()),
      ],
      child: const AvatarStudioApp(),
    ),
  );
}

class AvatarStudioApp extends StatelessWidget {
  const AvatarStudioApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AvatarAI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        primaryColor: const Color(0xFF6C5CE7),
        scaffoldBackgroundColor: const Color(0xFF0D0D0D),
        fontFamily: "Inter",
      ),
      home: const HomeScreen(),
    );
  }
}
