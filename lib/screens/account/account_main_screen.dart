import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:lithub_mobile/providers/auth_provider.dart';
import 'package:lithub_mobile/services/api_service.dart';

class AccountMainScreen extends StatelessWidget {
  const AccountMainScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final user = Provider.of<AuthProvider>(context).user ?? {};
    
    Widget profileImage = CircleAvatar(
      radius: 40,
      backgroundColor: Colors.grey[200],
      backgroundImage: user['profile_picture'] != null
                          ? NetworkImage('${ApiService.baseUrl}/static/images/profile/${user['profile_picture']}')
                          : const AssetImage('assets/default_avatar.png') as ImageProvider,
    );

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Account'),
        backgroundColor: Colors.deepPurple,
        foregroundColor: Colors.white,
      ),
      body: Container(
        color: Colors.grey[100],
        child: Column(
          children: [
            // Profile Section
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 24),
              decoration: const BoxDecoration(
                color: Colors.deepPurple,
                borderRadius: BorderRadius.only(
                  bottomLeft: Radius.circular(20),
                  bottomRight: Radius.circular(20),
                ),
              ),
              child: Column(
                children: [
                  profileImage,
                  const SizedBox(height: 12),
                  Text(
                    user['name'] ?? 'Guest',
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 4),
                  GestureDetector(
                    onTap: () => Navigator.pushNamed(context, '/account/profile'),
                    child: const Text(
                      'Edit profile',
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.white70,
                        decoration: TextDecoration.underline,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            
            // Navigation Menu
            Expanded(
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  // My Account Section
                  _buildExpandableSection(
                    context,
                    title: 'My Account',
                    icon: Icons.person_outline,
                    children: [
                      _buildNavItem(
                        context,
                        title: 'Profile',
                        icon: Icons.account_circle_outlined,
                        onTap: () => Navigator.pushNamed(context, '/account/edit'),
                      ),
                      _buildNavItem(
                        context,
                        title: 'Banks & Cards',
                        icon: Icons.credit_card_outlined,
                        onTap: () => Navigator.pushNamed(context, '/account/bank'),
                      ),
                      _buildNavItem(
                        context,
                        title: 'Address',
                        icon: Icons.location_on_outlined,
                        onTap: () => Navigator.pushNamed(context, '/account/address'),
                      ),
                      _buildNavItem(
                        context,
                        title: 'Change Password',
                        icon: Icons.lock_outline,
                        onTap: () => Navigator.pushNamed(context, '/account/password'),
                      ),
                    ],
                  ),
                  
                  const SizedBox(height: 8),
                  
                  // My Purchase
                  _buildNavItem(
                    context,
                    title: 'My Purchase',
                    icon: Icons.shopping_bag_outlined,
                    onTap: () => Navigator.pushNamed(context, '/account/purchases'),
                    isMainItem: true,
                  ),
                  
                  const SizedBox(height: 8),
                  
                  // Start Selling
                  _buildNavItem(
                    context,
                    title: 'Start Selling',
                    icon: Icons.store_outlined,
                    onTap: () => Navigator.pushNamed(context, '/seller/register'),
                    isMainItem: true,
                  ),
                  
                  const SizedBox(height: 24),
                  
                  // Logout
                  _buildNavItem(
                    context,
                    title: 'Log Out',
                    icon: Icons.logout,
                    onTap: () => _showLogoutModal(context),
                    isMainItem: true,
                    isDestructive: true,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildExpandableSection(
    BuildContext context, {
    required String title,
    required IconData icon,
    required List<Widget> children,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Theme(
        data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
        child: ExpansionTile(
          leading: Icon(icon, color: Colors.deepPurple),
          title: Text(
            title,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w500,
            ),
          ),
          iconColor: Colors.deepPurple,
          collapsedIconColor: Colors.black87,
          backgroundColor: Colors.white,
          collapsedBackgroundColor: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          children: children,
        ),
      ),
    );
  }
  
  Widget _buildNavItem(
    BuildContext context, {
    required String title,
    required IconData icon,
    required VoidCallback onTap,
    bool isMainItem = false,
    bool isDestructive = false,
  }) {
    final color = isDestructive ? Colors.red : Colors.deepPurple;
    
    return Card(
      margin: EdgeInsets.only(
        left: isMainItem ? 0 : 16,
        bottom: 4,
      ),
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      color: isMainItem ? Colors.white : Colors.deepPurple.withOpacity(0.05),
      child: ListTile(
        onTap: onTap,
        leading: Icon(
          icon,
          color: isMainItem ? color : Colors.deepPurple,
        ),
        title: Text(
          title,
          style: TextStyle(
            fontSize: isMainItem ? 16 : 15,
            fontWeight: isMainItem ? FontWeight.w500 : FontWeight.normal,
            color: isDestructive ? Colors.red : Colors.black87,
          ),
        ),
        trailing: isMainItem ? const Icon(Icons.chevron_right) : null,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
  }
  
  void _showLogoutModal(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.red.shade100,
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.logout, color: Colors.red),
            ),
            const SizedBox(width: 16),
            const Text('Log Out'),
          ],
        ),
        content: const Text('Are you sure you want to log out?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Provider.of<AuthProvider>(context, listen: false).logout();
              Navigator.pushNamedAndRemoveUntil(context, '/login', (route) => false);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            child: const Text('Yes, Log Out'),
          ),
        ],
      ),
    );
  }
}
