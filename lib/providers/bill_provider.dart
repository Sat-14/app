import 'package:flutter/material.dart';
import '../models/bill.dart';
import '../services/api_service.dart';
import '../services/notification_service.dart';

class BillProvider extends ChangeNotifier {
  List<Bill> _bills = [];
  bool _isLoading = false;
  String? _error;
  String _searchQuery = '';
  BillCategory? _selectedCategory;

  List<Bill> get bills => _bills;
  bool get isLoading => _isLoading;
  String? get error => _error;
  BillCategory? get selectedCategory => _selectedCategory;

  List<Bill> get filteredBills {
    return _bills.where((bill) {
      final matchesSearch = bill.name.toLowerCase().contains(_searchQuery.toLowerCase());
      final matchesCategory = _selectedCategory == null || bill.category == _selectedCategory;
      return matchesSearch && matchesCategory;
    }).toList();
  }

  List<Bill> get upcomingBills {
    final now = DateTime.now();
    final weekLater = now.add(const Duration(days: 7));
    return _bills.where((bill) {
      return !bill.isPaid && 
             bill.dueDate.isAfter(now) && 
             bill.dueDate.isBefore(weekLater);
    }).toList()..sort((a, b) => a.dueDate.compareTo(b.dueDate));
  }

  List<Bill> get overdueBills {
    final now = DateTime.now();
    return _bills.where((bill) {
      return !bill.isPaid && bill.dueDate.isBefore(now);
    }).toList()..sort((a, b) => a.dueDate.compareTo(b.dueDate));
  }

  double get totalMonthlyAmount {
    return _bills
        .where((bill) => bill.frequency == BillFrequency.monthly && !bill.isPaid)
        .fold(0, (sum, bill) => sum + bill.amount);
  }

  Map<BillCategory, double> get categoryBreakdown {
    final Map<BillCategory, double> breakdown = {};
    for (final bill in _bills.where((b) => !b.isPaid)) {
      breakdown[bill.category] = (breakdown[bill.category] ?? 0) + bill.amount;
    }
    return breakdown;
  }

  void setSearchQuery(String query) {
    _searchQuery = query;
    notifyListeners();
  }

  void setSelectedCategory(BillCategory? category) {
    _selectedCategory = category;
    notifyListeners();
  }

  Future<void> fetchBills() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _bills = await ApiService.getBills();
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> addBill(Bill bill) async {
    try {
      final newBill = await ApiService.createBill(bill);
      _bills.add(newBill);
      
      // Schedule notifications for the new bill
      await NotificationService.scheduleAllBillReminders(newBill);
      
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      rethrow;
    }
  }

  Future<void> updateBill(Bill bill) async {
    try {
      final updatedBill = await ApiService.updateBill(bill.id!, bill);
      final index = _bills.indexWhere((b) => b.id == bill.id);
      if (index != -1) {
        _bills[index] = updatedBill;
        
        // Reschedule notifications
        await NotificationService.cancelBillReminders(bill.id!);
        await NotificationService.scheduleAllBillReminders(updatedBill);
        
        notifyListeners();
      }
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      rethrow;
    }
  }

  Future<void> deleteBill(String id) async {
    try {
      await ApiService.deleteBill(id);
      
      // Cancel notifications
      await NotificationService.cancelBillReminders(id);
      
      _bills.removeWhere((bill) => bill.id == id);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      rethrow;
    }
  }

  Future<void> markAsPaid(String id) async {
    try {
      await ApiService.markBillAsPaid(id);
      final index = _bills.indexWhere((b) => b.id == id);
      if (index != -1) {
        _bills[index] = _bills[index].copyWith(isPaid: true);
        
        // Cancel notifications for paid bill
        await NotificationService.cancelBillReminders(id);
        
        notifyListeners();
      }
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      rethrow;
    }
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}