import 'package:flutter/material.dart';

class GenerationScreen extends StatefulWidget {
  const GenerationScreen({super.key});

  @override
  State<GenerationScreen> createState() => _GenerationScreenState();
}

class _GenerationScreenState extends State<GenerationScreen> {
  int _selectedStyle = 0;
  final List<Map<String, dynamic>> _styles = [
    {"name": "Anime", "icon": "🎨"},
    {"name": "3D", "icon": "🎭"},
    {"name": "Pixel", "icon": "👾"},
    {"name": "Pro", "icon": "👔"},
    {"name": "Cartoon", "icon": "🎪"},
    {"name": "Cyber", "icon": "🤖"},
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Выбери стиль"),
        backgroundColor: Colors.transparent,
      ),
      body: Column(
        children: [
          Expanded(
            child: GridView.builder(
              padding: const EdgeInsets.all(16),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
              ),
              itemCount: _styles.length,
              itemBuilder: (ctx, index) {
                final style = _styles[index];
                final isSelected = _selectedStyle == index;
                return GestureDetector(
                  onTap: () => setState(() => _selectedStyle = index),
                  child: Container(
                    decoration: BoxDecoration(
                      color: isSelected
                        ? const Color(0xFF6C5CE7)
                        : const Color(0xFF1E1E2E),
                      borderRadius: BorderRadius.circular(16),
                      border: isSelected
                        ? Border.all(color: const Color(0xFFFD79A8), width: 2)
                        : null,
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(style["icon"], style: const TextStyle(fontSize: 48)),
                        const SizedBox(height: 8),
                        Text(style["name"],
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(24.0),
            child: ElevatedButton(
              onPressed: () {
                Navigator.pushNamed(context, "/results");
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF6C5CE7),
                minimumSize: const Size(double.infinity, 56),
              ),
              child: const Text("Сгенерировать 🚀"),
            ),
          ),
        ],
      ),
    );
  }
}
