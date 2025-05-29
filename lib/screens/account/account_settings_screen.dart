import 'package:flutter/material.dart';

class AccountSettingsScreen extends StatelessWidget {
  const AccountSettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Account Settings'),
        backgroundColor: Colors.deepPurple,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          _buildSettingsTile(
            context,
            icon: Icons.person,
            title: 'Profile',
            subtitle: 'Edit and update your profile',
            route: '/account/edit',
          ),
          _buildSettingsTile(
            context,
            icon: Icons.credit_card,
            title: 'Banks and Cards',
            subtitle: 'Pay bills',
          ),
          _buildSettingsTile(
            context,
            icon: Icons.location_on,
            title: 'Address',
            subtitle: 'Update your address',
          ),
          _buildSettingsTile(
            context,
            icon: Icons.lock,
            title: 'Change Password',
            subtitle: 'Update your credentials',
          ),
        ],
      ),
    );
  }

  Widget _buildSettingsTile(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String subtitle,
    String? route,
  }) {
    return Card(
      elevation: 0.5,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      margin: const EdgeInsets.only(bottom: 16),
      child: ListTile(
        leading: Icon(icon, color: Colors.deepPurple),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
        subtitle: Text(subtitle),
        trailing: const Icon(Icons.arrow_forward_ios, size: 16),
        onTap: route != null ? () => Navigator.pushNamed(context, route) : null,
      ),
    );
  }
}
