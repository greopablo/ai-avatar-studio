import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  final String baseUrl = "http://localhost:8000/api";
  
  Future<Map<String, dynamic>> register(String phone) async {
    final response = await http.post(
      Uri.parse("$baseUrl/auth/register"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"phone": phone}),
    );
    return jsonDecode(response.body);
  }
  
  Future<Map<String, dynamic>> login(String phone, String code) async {
    final response = await http.post(
      Uri.parse("$baseUrl/auth/login"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"phone": phone, "code": code}),
    );
    return jsonDecode(response.body);
  }
  
  Future<List<dynamic>> getAvatars(String token) async {
    final response = await http.get(
      Uri.parse("$baseUrl/users/me/avatars"),
      headers: {"Authorization": "Bearer $token"},
    );
    return jsonDecode(response.body);
  }
}
