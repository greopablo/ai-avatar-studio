class User {
  final String id;
  final String phone;
  final bool isPremium;
  final int credits;
  
  User({
    required this.id,
    required this.phone,
    required this.isPremium,
    required this.credits,
  });
  
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json["id"],
      phone: json["phone"],
      isPremium: json["is_premium"] ?? false,
      credits: json["credits"] ?? 3,
    );
  }
}
