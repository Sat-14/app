import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../models/bill.dart';
import '../../config/theme.dart';

class CategoryPieChart extends StatefulWidget {
  final Map<BillCategory, double> categoryBreakdown;

  const CategoryPieChart({
    super.key,
    required this.categoryBreakdown,
  });

  @override
  _CategoryPieChartState createState() => _CategoryPieChartState();
}

class _CategoryPieChartState extends State<CategoryPieChart> {
  int touchedIndex = -1;

  @override
  Widget build(BuildContext context) {
    if (widget.categoryBreakdown.isEmpty) {
      return const Center(
        child: Text(
          'No data available',
          style: TextStyle(color: Colors.grey),
        ),
      );
    }

    return PieChart(
      PieChartData(
        pieTouchData: PieTouchData(
          touchCallback: (FlTouchEvent event, pieTouchResponse) {
            setState(() {
              if (!event.isInterestedForInteractions ||
                  pieTouchResponse == null ||
                  pieTouchResponse.touchedSection == null) {
                touchedIndex = -1;
                return;
              }
              touchedIndex = pieTouchResponse.touchedSection!.touchedSectionIndex;
            });
          },
        ),
        borderData: FlBorderData(show: false),
        sectionsSpace: 2,
        centerSpaceRadius: 40,
        sections: _buildSections(),
      ),
    );
  }

  List<PieChartSectionData> _buildSections() {
    final total = widget.categoryBreakdown.values.fold(0.0, (sum, value) => sum + value);
    
    return widget.categoryBreakdown.entries.map((entry) {
      final index = widget.categoryBreakdown.keys.toList().indexOf(entry.key);
      final isTouched = index == touchedIndex;
      final fontSize = isTouched ? 16.0 : 14.0;
      final radius = isTouched ? 65.0 : 60.0;
      final percentage = (entry.value / total * 100).toStringAsFixed(1);
      final categoryName = entry.key.toString().split('.').last;
      final color = AppTheme.categoryColors[categoryName]!;

      return PieChartSectionData(
        color: color,
        value: entry.value,
        title: '$percentage%',
        radius: radius,
        titleStyle: TextStyle(
          fontSize: fontSize,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      );
    }).toList();
  }
}