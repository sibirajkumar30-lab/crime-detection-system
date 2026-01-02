import React from 'react';
import { Box, Paper, Typography } from '@mui/material';

const PieChart = ({ data, title, labelKey, valueKey }) => {
    if (!data || data.length === 0) {
        return (
            <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>{title}</Typography>
                <Typography color="text.secondary">No data available</Typography>
            </Paper>
        );
    }

    const total = data.reduce((sum, item) => sum + (item[valueKey] || 0), 0);
    const colors = ['#1976d2', '#2e7d32', '#ed6c02', '#d32f2f', '#9c27b0', '#0288d1'];

    let currentAngle = -90; // Start at top

    return (
        <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>{title}</Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mt: 2, flexWrap: 'wrap' }}>
                {/* Pie Chart */}
                <Box sx={{ position: 'relative', width: 200, height: 200, mr: 3 }}>
                    <svg width="200" height="200" viewBox="0 0 200 200">
                        {data.map((item, index) => {
                            const value = item[valueKey] || 0;
                            const percentage = total > 0 ? (value / total) * 100 : 0;
                            const angle = (percentage / 100) * 360;
                            
                            const startAngle = currentAngle;
                            const endAngle = currentAngle + angle;
                            currentAngle = endAngle;

                            // Convert angles to radians
                            const startRad = (startAngle * Math.PI) / 180;
                            const endRad = (endAngle * Math.PI) / 180;

                            // Calculate arc path
                            const x1 = 100 + 80 * Math.cos(startRad);
                            const y1 = 100 + 80 * Math.sin(startRad);
                            const x2 = 100 + 80 * Math.cos(endRad);
                            const y2 = 100 + 80 * Math.sin(endRad);

                            const largeArcFlag = angle > 180 ? 1 : 0;

                            const pathData = [
                                `M 100 100`,
                                `L ${x1} ${y1}`,
                                `A 80 80 0 ${largeArcFlag} 1 ${x2} ${y2}`,
                                `Z`
                            ].join(' ');

                            return (
                                <path
                                    key={index}
                                    d={pathData}
                                    fill={colors[index % colors.length]}
                                    stroke="#fff"
                                    strokeWidth="2"
                                />
                            );
                        })}
                    </svg>
                </Box>

                {/* Legend */}
                <Box>
                    {data.map((item, index) => {
                        const value = item[valueKey] || 0;
                        const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                        
                        return (
                            <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <Box
                                    sx={{
                                        width: 16,
                                        height: 16,
                                        backgroundColor: colors[index % colors.length],
                                        borderRadius: 1,
                                        mr: 1
                                    }}
                                />
                                <Typography variant="body2" color="text.secondary">
                                    {item[labelKey]}: {value} ({percentage}%)
                                </Typography>
                            </Box>
                        );
                    })}
                </Box>
            </Box>
        </Paper>
    );
};

export default PieChart;
