import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import '../../models/bill.dart';
import '../../config/theme.dart';

class MonthlyTrendChart extends StatelessWidget {
  final List<Bill> bills;

  const MonthlyTrendChart({
    super.key,
    required this.bills,
  });

  @override
  Widget build(BuildContext context) {
    final monthlyData = _calculateMonthlyData();
    
    if (monthlyData.isEmpty) {
      return const Center(
        child: Text(
          'No data available',
          style: TextStyle(color: Colors.grey),
        ),
      );
    }

    return LineChart(
      LineChartData(
        gridData: FlGridData(
          show: true,
          drawVerticalLine: false,
          horizontalInterval: 1,
          getDrawingHorizontalLine: (value) {
            return FlLine(
              color: Colors.grey.withOpacity(0.2),
              strokeWidth: 1,
            );
          },
        ),
        titlesData: FlTitlesData(
          show: true,
          rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              interval: 1,
              getTitlesWidget: (value, meta) {
                return Text(
                  '\$${value.toInt()}',
                  style: const TextStyle(
                    color: Colors.grey,
                    fontSize: 12,
                  ),
                );
              },
              reservedSize: 42,
            ),
          ),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                if (value.toInt() >= 0 && value.toInt() < monthlyData.length) {
                  return Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text(
                      monthlyData[value.toInt()].month,
                      style: const TextStyle(
                        color: Colors.grey,
                        fontSize: 12,
                      ),
                    ),
                  );
                }
                return Container();
              },
              interval: 1,
            ),
          ),
        ),
        borderData: FlBorderData(show: false),
        minX: 0,
        maxX: monthlyData.length - 1.0,
        minY: 0,
        maxY: _getMaxY(monthlyData),
        lineBarsData: [
          LineChartBarData(
            spots: monthlyData.asMap().entries.map((entry) {
              return FlSpot(entry.key.toDouble(), entry.value.amount);
            }).toList(),
            isCurved: true,
            color: AppTheme.primaryColor,
            barWidth: 3,
            isStrokeCapRound: true,
            dotData: FlDotData(
              show: true,
              getDotPainter: (spot, percent, barData, index) {
                return FlDotCirclePainter(
                  radius: 4,
                  color: AppTheme.primaryColor,
                  strokeWidth: 2,
                  strokeColor: Colors.white,
                );
              },
            ),
            belowBarData: BarAreaData(
              show: true,
              color: AppTheme.primaryColor.withOpacity(0.1),
            ),
          ),
        ],
      ),
    );
  }

  List<MonthlyData> _calculateMonthlyData() {
    final now = DateTime.now();
    final Map<String, double> monthlyTotals = {};
    
    // Get last 6 months
    for (int i = 5; i >= 0; i--) {
      final month = DateTime(now.year, now.month - i, 1);
      final monthKey = DateFormat('MMM').format(month);
      monthlyTotals[monthKey] = 0;
    }

    // Calculate totals
    for (final bill in bills) {
      final monthKey = DateFormat('MMM').format(bill.dueDate);
      if (monthlyTotals.containsKey(monthKey)) {
        monthlyTotals[monthKey] = monthlyTotals[monthKey]! + bill.amount;
      }
    }

    return monthlyTotals.entries
        .map((e) => MonthlyData(month: e.key, amount: e.value))
        .toList();
  }

  double _getMaxY(List<MonthlyData> data) {
    final maxAmount = data.map((e) => e.amount).reduce((a, b) => a > b ? a : b);
    return (maxAmount * 1.2 / 100).ceil() * 100; // Round up to nearest 100
  }
}

class MonthlyData {
  final String month;
  final double amount;

  MonthlyData({required this.month, required this.amount});
}