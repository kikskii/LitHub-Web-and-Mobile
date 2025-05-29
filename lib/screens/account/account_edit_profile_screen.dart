import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import 'package:lithub_mobile/providers/auth_provider.dart';
import 'package:lithub_mobile/services/api_service.dart';

class AccountEditProfileScreen extends StatefulWidget {
  const AccountEditProfileScreen({Key? key}) : super(key: key);

  @override
  State<AccountEditProfileScreen> createState() => _AccountEditProfileScreenState();
}

class _AccountEditProfileScreenState extends State<AccountEditProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  bool _isEditing = false;
  bool _isLoading = false;
  File? _imageFile;
  final ImagePicker _picker = ImagePicker();
  
  // Form controllers
  late TextEditingController _nameController;
  late TextEditingController _emailController;
  late TextEditingController _phoneController;
  late TextEditingController _dobController;
  String _gender = 'M'; // Default value
  
  @override
  void initState() {
    super.initState();
    final user = Provider.of<AuthProvider>(context, listen: false).user ?? {};
    print('Debug - User Data in initState: $user');
    
    _nameController = TextEditingController(text: user['name']?.toString() ?? '');
    _emailController = TextEditingController(text: user['email']?.toString() ?? '');
    _phoneController = TextEditingController(text: user['phone']?.toString() ?? '');
    _dobController = TextEditingController(text: user['date_of_birth']?.toString() ?? '');
    _gender = user['gender']?.toString() ?? 'M';
  }
  
  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _dobController.dispose();
    super.dispose();
  }
  
  Future<void> _pickImage() async {
    try {
      final XFile? image = await _picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 800,
        maxHeight: 800,
        imageQuality: 85,
      );
      
      if (image != null) {
        setState(() {
          _imageFile = File(image.path);
        });
        
        // Upload image immediately
        _uploadProfilePicture();
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error picking image: $e')),
      );
    }
  }
  
  Future<void> _uploadProfilePicture() async {
    if (_imageFile == null) return;
    
    setState(() {
      _isLoading = true;
    });
    
    try {
      final result = await ApiService.updateProfilePicture(_imageFile!);
      
      if (result['success']) {
        // Update the user profile in provider
        final authProvider = Provider.of<AuthProvider>(context, listen: false);
        await authProvider.refreshUserProfile();
        
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Profile picture updated successfully')),
        );
      } else {
        throw Exception(result['error'] ?? 'Failed to update profile picture');
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }
  
  Future<void> _updateProfile() async {
    if (!_formKey.currentState!.validate()) return;
    
    setState(() {
      _isLoading = true;
    });
    
    try {
      final userData = {
        'name': _nameController.text,
        'phone': _phoneController.text,
        'gender': _gender,
        'date_of_birth': _dobController.text,
      };
      
      final result = await ApiService.updateProfile(userData);
      
      if (result['success']) {
        // Update the user profile in provider
        final authProvider = Provider.of<AuthProvider>(context, listen: false);
        await authProvider.refreshUserProfile();
        
        setState(() {
          _isEditing = false;
        });
        
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Profile updated successfully')),
        );
      } else {
        throw Exception(result['error'] ?? 'Failed to update profile');
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }
  
  void _toggleEdit() {
    setState(() {
      _isEditing = !_isEditing;
      
      // If canceling edit, reset form values
      if (!_isEditing) {
        final user = Provider.of<AuthProvider>(context, listen: false).user ?? {};
        _nameController.text = user['name']?.toString() ?? '';
        _phoneController.text = user['phone']?.toString() ?? '';
        _dobController.text = user['date_of_birth']?.toString() ?? '';
        _gender = user['gender']?.toString() ?? 'M';
      }
    });
  }
  
  @override
  Widget build(BuildContext context) {
    final user = Provider.of<AuthProvider>(context).user ?? {};
    print('Debug - Build User Data: $user');
    print('Debug - Profile Picture URL: ${user['profile_picture']}');
    
    Widget profileWidget;
    if (user['profile_picture'] != null && user['profile_picture'].toString().isNotEmpty) {
      final imageUrl = '${ApiService.baseUrl}/static/images/profile/${user['profile_picture']}';
      print('Debug - Full Image URL: $imageUrl');
      
      profileWidget = CircleAvatar(
        radius: 100,
        backgroundColor: Colors.grey[200],
        child: ClipOval(
          child: Image.network(
            imageUrl,
            width: 200,
            height: 200,
            fit: BoxFit.cover,
            errorBuilder: (context, error, stackTrace) {
              print('Error loading profile picture: $error');
              return const Icon(Icons.person, size: 80, color: Colors.grey);
            },
            loadingBuilder: (context, child, loadingProgress) {
              if (loadingProgress == null) return child;
              return Center(
                child: CircularProgressIndicator(
                  value: loadingProgress.expectedTotalBytes != null
                      ? loadingProgress.cumulativeBytesLoaded / loadingProgress.expectedTotalBytes!
                      : null,
                ),
              );
            },
          ),
        ),
      );
    } else {
      profileWidget = CircleAvatar(
        radius: 100,
        backgroundColor: Colors.grey[200],
        child: const Icon(Icons.person, size: 80, color: Colors.grey),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Profile'),
        backgroundColor: Colors.deepPurple,
        foregroundColor: Colors.white,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: Column(
                  children: [
                    Container(
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(16),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.08),
                            blurRadius: 20,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(20.0),
                        child: Column(
                          children: [
                            // Profile picture section
                            GestureDetector(
                              onTap: _pickImage,
                              child: Stack(
                                alignment: Alignment.center,
                                children: [
                                  ClipOval(
                                    child: Container(
                                      width: 200,
                                      height: 200,
                                      decoration: BoxDecoration(
                                        shape: BoxShape.circle,
                                        border: Border.all(
                                          color: Colors.deepPurple,
                                          width: 4,
                                        ),
                                      ),
                                      child: profileWidget,
                                    ),
                                  ),
                                  Positioned(
                                    bottom: 0,
                                    right: 0,
                                    child: Container(
                                      padding: const EdgeInsets.all(8),
                                      decoration: const BoxDecoration(
                                        color: Colors.deepPurple,
                                        shape: BoxShape.circle,
                                      ),
                                      child: const Icon(
                                        Icons.camera_alt,
                                        color: Colors.white,
                                        size: 20,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 20),
                            
                            // Profile form
                            Form(
                              key: _formKey,
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  _buildFormField(
                                    label: 'Name',
                                    controller: _nameController,
                                    enabled: _isEditing,
                                    validator: (value) {
                                      if (value == null || value.isEmpty) {
                                        return 'Please enter your name';
                                      }
                                      return null;
                                    },
                                  ),
                                  _buildFormField(
                                    label: 'Email',
                                    controller: _emailController,
                                    enabled: false, // Email is always disabled
                                    keyboardType: TextInputType.emailAddress,
                                  ),
                                  _buildFormField(
                                    label: 'Phone Number',
                                    controller: _phoneController,
                                    enabled: _isEditing,
                                    keyboardType: TextInputType.phone,
                                  ),
                                  const SizedBox(height: 16),
                                  
                                  // Gender selection
                                  Wrap(
                                    crossAxisAlignment: WrapCrossAlignment.center,
                                    children: [
                                      Text('Gender: ', style: TextStyle(fontWeight: FontWeight.bold)),
                                      Radio<String>(
                                        value: 'M',
                                        groupValue: _gender,
                                        onChanged: _isEditing ? (value) {
                                          setState(() {
                                            _gender = value!;
                                          });
                                        } : null,
                                      ),
                                      Text('Male'),
                                      Radio<String>(
                                        value: 'F',
                                        groupValue: _gender,
                                        onChanged: _isEditing ? (value) {
                                          setState(() {
                                            _gender = value!;
                                          });
                                        } : null,
                                      ),
                                      Text('Female'),
                                    ],
                                  ),
                                  const SizedBox(height: 16),
                                  
                                  // Date of birth
                                  _buildFormField(
                                    label: 'Date of Birth',
                                    controller: _dobController,
                                    enabled: _isEditing,
                                    onTap: _isEditing ? () async {
                                      final date = await showDatePicker(
                                        context: context,
                                        initialDate: DateTime.now().subtract(const Duration(days: 365 * 18)),
                                        firstDate: DateTime(1900),
                                        lastDate: DateTime.now(),
                                      );
                                      if (date != null) {
                                        setState(() {
                                          _dobController.text = "${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}";
                                        });
                                      }
                                    } : null,
                                    readOnly: true,
                                    suffixIcon: _isEditing ? const Icon(Icons.calendar_today) : null,
                                  ),
                                  const SizedBox(height: 30),
                                  
                                  // Action buttons
                                  Row(
                                    children: [
                                      Expanded(
                                        child: ElevatedButton(
                                          onPressed: _toggleEdit,
                                          style: ElevatedButton.styleFrom(
                                            backgroundColor: _isEditing ? Colors.grey.shade200 : Colors.white,
                                            foregroundColor: Colors.deepPurple,
                                            side: const BorderSide(color: Colors.deepPurple, width: 2),
                                            padding: const EdgeInsets.symmetric(vertical: 16),
                                            shape: RoundedRectangleBorder(
                                              borderRadius: BorderRadius.circular(8),
                                            ),
                                          ),
                                          child: Row(
                                            mainAxisAlignment: MainAxisAlignment.center,
                                            children: [
                                              Icon(_isEditing ? Icons.close : Icons.edit),
                                              const SizedBox(width: 8),
                                              Text(_isEditing ? 'Cancel' : 'Edit'),
                                            ],
                                          ),
                                        ),
                                      ),
                                      if (_isEditing) ...[
                                        const SizedBox(width: 16),
                                        Expanded(
                                          child: ElevatedButton(
                                            onPressed: _updateProfile,
                                            style: ElevatedButton.styleFrom(
                                              backgroundColor: Colors.deepPurple,
                                              foregroundColor: Colors.white,
                                              padding: const EdgeInsets.symmetric(vertical: 16),
                                              shape: RoundedRectangleBorder(
                                                borderRadius: BorderRadius.circular(8),
                                              ),
                                            ),
                                            child: const Text('Save Changes'),
                                          ),
                                        ),
                                      ],
                                    ],
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
    );
  }
  
  Widget _buildFormField({
    required String label,
    required TextEditingController controller,
    bool enabled = true,
    TextInputType keyboardType = TextInputType.text,
    String? Function(String?)? validator,
    VoidCallback? onTap,
    bool readOnly = false,
    Widget? suffixIcon,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w500,
            color: Color(0xFF2D3436),
          ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          controller: controller,
          enabled: enabled,
          keyboardType: keyboardType,
          validator: validator,
          onTap: onTap,
          readOnly: readOnly,
          decoration: InputDecoration(
            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide(color: Colors.grey.shade300, width: 1.5),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide(color: Colors.grey.shade300, width: 1.5),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: const BorderSide(color: Colors.deepPurple, width: 1.5),
            ),
            filled: true,
            fillColor: enabled ? Colors.white : Colors.grey.shade100,
            suffixIcon: suffixIcon,
          ),
          style: TextStyle(
            color: enabled ? Colors.black87 : Colors.grey.shade700,
          ),
        ),
        const SizedBox(height: 16),
      ],
    );
  }
}