import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/bill.dart';
import '../../providers/bill_provider.dart';
import '../../widgets/bills/bill_list_item.dart';
import '../../widgets/bills/bill_filter_chip.dart';
import 'add_edit_bill_screen.dart';
import 'package:final_wali_file/extensions/string_extensions.dart';


class BillsListScreen extends StatefulWidget {
  const BillsListScreen({super.key});

  @override
  _BillsListScreenState createState() => _BillsListScreenState();
}

class _BillsListScreenState extends State<BillsListScreen> {
  final _searchController = TextEditingController();

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final billProvider = context.watch<BillProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Bills'),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () {
              // Toggle search
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Search bar
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Search bills...',
                prefixIcon: const Icon(Icons.search),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                contentPadding: const EdgeInsets.symmetric(horizontal: 16),
              ),
              onChanged: (value) {
                billProvider.setSearchQuery(value);
              },
            ),
          ),

          // Category filters
          SizedBox(
            height: 50,
            child: ListView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              children: [
                BillFilterChip(
                  label: 'All',
                  isSelected: billProvider.selectedCategory == null,
                  onSelected: () {
                    billProvider.setSelectedCategory(null);
                  },
                ),
                ...BillCategory.values.map((category) => Padding(
                  padding: const EdgeInsets.only(left: 8),
                  child: BillFilterChip(
                    label: category.toString().split('.').last.capitalize(),
                    isSelected: billProvider.selectedCategory == category,
                    onSelected: () {
                      billProvider.setSelectedCategory(category);
                    },
                  ),
                )),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Bills list
          Expanded(
            child: billProvider.isLoading
                ? const Center(child: CircularProgressIndicator())
                : billProvider.filteredBills.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.receipt_long, size: 64, color: Colors.grey),
                            const SizedBox(height: 16),
                            const Text('No bills found', style: TextStyle(fontSize: 18, color: Colors.grey)),
                            const SizedBox(height: 8),
                            ElevatedButton(
                              onPressed: () {
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (context) => const AddEditBillScreen(),
                                  ),
                                );
                              },
                              child: const Text('Add Your First Bill'),
                            ),
                          ],
                        ),
                      )
                    : RefreshIndicator(
                        onRefresh: () => billProvider.fetchBills(),
                        child: ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: billProvider.filteredBills.length,
                          itemBuilder: (context, index) {
                            final bill = billProvider.filteredBills[index];
                            return Padding(
                              padding: const EdgeInsets.only(bottom: 8),
                              child: BillListItem(
                                bill: bill,
                                onTap: () {
                                  Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                      builder: (context) => AddEditBillScreen(bill: bill),
                                    ),
                                  );
                                },
                                onDelete: () async {
                                  final confirmed = await showDialog<bool>(
                                    context: context,
                                    builder: (context) => AlertDialog(
                                      title: const Text('Delete Bill'),
                                      content: const Text('Are you sure you want to delete this bill?'),
                                      actions: [
                                        TextButton(
                                          onPressed: () => Navigator.pop(context, false),
                                          child: const Text('Cancel'),
                                        ),
                                        TextButton(
                                          onPressed: () => Navigator.pop(context, true),
                                          style: TextButton.styleFrom(
                                            foregroundColor: Colors.red,
                                          ),
                                          child: const Text('Delete'),
                                        ),
                                      ],
                                    ),
                                  );

                                  if (confirmed == true) {
                                    await billProvider.deleteBill(bill.id!);
                                  }
                                },
                                onMarkPaid: () async {
                                  await billProvider.markAsPaid(bill.id!);
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(
                                      content: Text('Bill marked as paid'),
                                      backgroundColor: Colors.green,
                                    ),
                                  );
                                },
                              ),
                            );
                          },
                        ),
                      ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const AddEditBillScreen()),
          );
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}

