import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/bill_provider.dart';
import '../../config/theme.dart';
import '../../widgets/analytics/category_pie_chart.dart';
import '../../widgets/analytics/monthly_trend_chart.dart';
import '../../widgets/analytics/stats_card.dart';
import 'package:final_wali_file/extensions/string_extensions.dart';


class AnalyticsScreen extends StatefulWidget {
  const AnalyticsScreen({super.key});

  @override
  _AnalyticsScreenState createState() => _AnalyticsScreenState();
}

class _AnalyticsScreenState extends State<AnalyticsScreen> {
  String _selectedPeriod = 'This Month';

  @override
  Widget build(BuildContext context) {
    final billProvider = context.watch<BillProvider>();

    // Calculate statistics
    final totalBills = billProvider.bills.length;
    final paidBills = billProvider.bills.where((b) => b.isPaid).length;
    final totalAmount = billProvider.bills
        .where((b) => !b.isPaid)
        .fold(0.0, (sum, bill) => sum + bill.amount);
    final averageAmount = totalBills > 0 ? totalAmount / totalBills : 0.0;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Analytics'),
        actions: [
          PopupMenuButton<String>(
            onSelected: (value) {
              setState(() {
                _selectedPeriod = value;
              });
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'This Month',
                child: Text('This Month'),
              ),
              const PopupMenuItem(
                value: 'Last 3 Months',
                child: Text('Last 3 Months'),
              ),
              const PopupMenuItem(
                value: 'This Year',
                child: Text('This Year'),
              ),
            ],
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Row(
                children: [
                  Text(_selectedPeriod),
                  const Icon(Icons.arrow_drop_down),
                ],
              ),
            ),
          ),
        ],
      ),
      body: billProvider.isLoading
          ? const Center(child: CircularProgressIndicator())
          : billProvider.bills.isEmpty
              ? const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.analytics,
                        size: 64,
                        color: Colors.grey,
                      ),
                      SizedBox(height: 16),
                      Text(
                        'No data to analyze',
                        style: TextStyle(
                          fontSize: 18,
                          color: Colors.grey,
                        ),
                      ),
                      SizedBox(height: 8),
                      Text(
                        'Add some bills to see analytics',
                        style: TextStyle(
                          color: Colors.grey,
                        ),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: () => billProvider.fetchBills(),
                  child: SingleChildScrollView(
                    physics: const AlwaysScrollableScrollPhysics(),
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Stats cards
                        Row(
                          children: [
                            Expanded(
                              child: StatsCard(
                                title: 'Total Bills',
                                value: totalBills.toString(),
                                icon: Icons.receipt_long,
                                color: AppTheme.primaryColor,
                              ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: StatsCard(
                                title: 'Paid Bills',
                                value: paidBills.toString(),
                                icon: Icons.check_circle,
                                color: AppTheme.paidColor,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        Row(
                          children: [
                            Expanded(
                              child: StatsCard(
                                title: 'Total Amount',
                                value: '\$${totalAmount.toStringAsFixed(2)}',
                                icon: Icons.attach_money,
                                color: AppTheme.warningColor,
                              ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: StatsCard(
                                title: 'Average Bill',
                                value: '\$${averageAmount.toStringAsFixed(2)}',
                                icon: Icons.analytics,
                                color: AppTheme.secondaryColor,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 32),

                        // Category breakdown
                        const Text(
                          'Spending by Category',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 16),
                        Card(
                          child: Padding(
                            padding: const EdgeInsets.all(16),
                            child: Column(
                              children: [
                                SizedBox(
                                  height: 200,
                                  child: CategoryPieChart(
                                    categoryBreakdown: billProvider.categoryBreakdown,
                                  ),
                                ),
                                const SizedBox(height: 16),
                                // Legend
                                ...billProvider.categoryBreakdown.entries.map(
                                  (entry) => Padding(
                                    padding: const EdgeInsets.symmetric(vertical: 4),
                                    child: Row(
                                      children: [
                                        Container(
                                          width: 16,
                                          height: 16,
                                          decoration: BoxDecoration(
                                            color: AppTheme.categoryColors[
                                                entry.key.toString().split('.').last],
                                            borderRadius: BorderRadius.circular(4),
                                          ),
                                        ),
                                        const SizedBox(width: 8),
                                        Expanded(
                                          child: Text(
                                            entry.key.toString().split('.').last.capitalize(),
                                          ),
                                        ),
                                        Text(
                                          '\$${entry.value.toStringAsFixed(2)}',
                                          style: const TextStyle(
                                            fontWeight: FontWeight.bold,
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
                        const SizedBox(height: 32),

                        // Monthly trend
                        const Text(
                          'Monthly Trend',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 16),
                        Card(
                          child: Padding(
                            padding: const EdgeInsets.all(16),
                            child: SizedBox(
                              height: 200,
                              child: MonthlyTrendChart(bills: billProvider.bills),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
    );
  }
}

