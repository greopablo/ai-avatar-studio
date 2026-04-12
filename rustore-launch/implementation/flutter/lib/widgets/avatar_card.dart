import 'package:flutter/material.dart';

class AvatarCard extends StatelessWidget {
  const AvatarCard({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF1E1E2E),
        borderRadius: BorderRadius.circular(12),
      ),
      child: const Center(
        child: Icon(
          Icons.person,
          color: Color(0xFF6C5CE7),
          size: 32,
        ),
      ),
    );
  }
}
