import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../models/bill.dart';
import '../../providers/bill_provider.dart';
import '../../utils/validators.dart';
import '../../config/theme.dart';
import 'package:final_wali_file/providers/auth_provider.dart';
import 'package:final_wali_file/extensions/string_extensions.dart';



class AddEditBillScreen extends StatefulWidget {
  final Bill? bill;

  const AddEditBillScreen({super.key, this.bill});

  @override
  _AddEditBillScreenState createState() => _AddEditBillScreenState();
}

class _AddEditBillScreenState extends State<AddEditBillScreen> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _nameController;
  late TextEditingController _amountController;
  late TextEditingController _notesController;
  late DateTime _selectedDate;
  late BillCategory _selectedCategory;
  late BillFrequency _selectedFrequency;
  bool _isLoading = false;
  
  // Reminder preferences
  bool _enableWhatsApp = true;
  bool _enableCall = false;
  bool _enableLocalNotification = true;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.bill?.name ?? '');
    _amountController = TextEditingController(
      text: widget.bill?.amount.toString() ?? '',
    );
    _notesController = TextEditingController(text: widget.bill?.notes ?? '');
    _selectedDate = widget.bill?.dueDate ?? DateTime.now();
    _selectedCategory = widget.bill?.category ?? BillCategory.utilities;
    _selectedFrequency = widget.bill?.frequency ?? BillFrequency.monthly;
    
    // Initialize reminder preferences
    if (widget.bill?.reminderPreferences != null) {
      _enableWhatsApp = widget.bill!.reminderPreferences!.enableWhatsApp;
      _enableCall = widget.bill!.reminderPreferences!.enableCall;
      _enableLocalNotification = widget.bill!.reminderPreferences!.enableLocalNotification;
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _amountController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _selectDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate,
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 365)),
    );

    if (picked != null) {
      setState(() {
        _selectedDate = picked;
      });
    }
  }

  Future<void> _saveBill() async {
    if (_formKey.currentState!.validate()) {
      setState(() {
        _isLoading = true;
      });

      try {
        final bill = Bill(
          id: widget.bill?.id,
          name: _nameController.text.trim(),
          amount: double.parse(_amountController.text),
          dueDate: _selectedDate,
          category: _selectedCategory,
          frequency: _selectedFrequency,
          notes: _notesController.text.trim(),
          isPaid: widget.bill?.isPaid ?? false,
          reminderPreferences: ReminderPreferences(
            enableWhatsApp: _enableWhatsApp,
            enableCall: _enableCall,
            enableLocalNotification: _enableLocalNotification,
            enableSMS: false,
          ),
        );

        final billProvider = context.read<BillProvider>();
        
        if (widget.bill == null) {
          await billProvider.addBill(bill);
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Bill added successfully'),
              backgroundColor: Colors.green,
            ),
          );
        } else {
          await billProvider.updateBill(bill);
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Bill updated successfully'),
              backgroundColor: Colors.green,
            ),
          );
        }

        Navigator.pop(context);
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(e.toString().replaceAll('Exception: ', '')),
            backgroundColor: Colors.red,
          ),
        );
      } finally {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final isEditing = widget.bill != null;

    return Scaffold(
      appBar: AppBar(
        title: Text(isEditing ? 'Edit Bill' : 'Add New Bill'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Bill name
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: 'Bill Name',
                  prefixIcon: Icon(Icons.receipt),
                ),
                validator: Validators.required,
              ),
              const SizedBox(height: 16),

              // Amount
              TextFormField(
                controller: _amountController,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: const InputDecoration(
                  labelText: 'Amount',
                  prefixIcon: Icon(Icons.attach_money),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter an amount';
                  }
                  if (double.tryParse(value) == null) {
                    return 'Please enter a valid amount';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // Due date
              InkWell(
                onTap: _selectDate,
                child: InputDecorator(
                  decoration: const InputDecoration(
                    labelText: 'Due Date',
                    prefixIcon: Icon(Icons.calendar_today),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(DateFormat('MMM dd, yyyy').format(_selectedDate)),
                      const Icon(Icons.arrow_drop_down),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Category
              DropdownButtonFormField<BillCategory>(
                value: _selectedCategory,
                decoration: const InputDecoration(
                  labelText: 'Category',
                  prefixIcon: Icon(Icons.category),
                ),
                items: BillCategory.values.map((category) {
                  return DropdownMenuItem(
                    value: category,
                    child: Row(
                      children: [
                        Container(
                          width: 16,
                          height: 16,
                          decoration: BoxDecoration(
                            color: AppTheme.categoryColors[
                                category.toString().split('.').last],
                            borderRadius: BorderRadius.circular(4),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(category.toString().split('.').last.capitalize()),
                      ],
                    ),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() {
                    _selectedCategory = value!;
                  });
                },
              ),
              const SizedBox(height: 16),

              // Frequency
              DropdownButtonFormField<BillFrequency>(
                value: _selectedFrequency,
                decoration: const InputDecoration(
                  labelText: 'Frequency',
                  prefixIcon: Icon(Icons.repeat),
                ),
                items: BillFrequency.values.map((frequency) {
                  return DropdownMenuItem(
                    value: frequency,
                    child: Text(frequency.toString().split('.').last.capitalize()),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() {
                    _selectedFrequency = value!;
                  });
                },
              ),
              const SizedBox(height: 16),

              // Notes
              TextFormField(
                controller: _notesController,
                maxLines: 3,
                decoration: const InputDecoration(
                  labelText: 'Notes (Optional)',
                  prefixIcon: Icon(Icons.note),
                  alignLabelWithHint: true,
                ),
              ),
              const SizedBox(height: 24),

              // Reminder preferences (only show if user has phone number)
              if (context.read<AuthProvider>().user?.phoneNumber != null &&
                  context.read<AuthProvider>().user!.phoneNumber!.isNotEmpty) ...[
                const Text(
                  'Reminder Preferences',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Choose how you want to be reminded for this bill',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                  ),
                ),
                const SizedBox(height: 16),
                Card(
                  child: Column(
                    children: [
                      CheckboxListTile(
                        title: const Text('Push Notifications'),
                        secondary: const Icon(Icons.notifications),
                        value: _enableLocalNotification,
                        onChanged: (value) {
                          setState(() {
                            _enableLocalNotification = value!;
                          });
                        },
                      ),
                      const Divider(height: 1),
                      CheckboxListTile(
                        title: const Text('WhatsApp Message'),
                        secondary: const Icon(Icons.message, color: Colors.green),
                        value: _enableWhatsApp,
                        onChanged: (value) {
                          setState(() {
                            _enableWhatsApp = value!;
                          });
                        },
                      ),
                      const Divider(height: 1),
                      CheckboxListTile(
                        title: const Text('Phone Call'),
                        secondary: const Icon(Icons.phone, color: Colors.blue),
                        value: _enableCall,
                        onChanged: (value) {
                          setState(() {
                            _enableCall = value!;
                          });
                        },
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
              ],

              // Save button
              ElevatedButton(
                onPressed: _isLoading ? null : _saveBill,
                child: _isLoading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                        ),
                      )
                    : Text(isEditing ? 'Update Bill' : 'Add Bill'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

