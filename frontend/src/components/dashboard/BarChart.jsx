import React from 'react';
import { Box, Paper, Typography } from '@mui/material';

const BarChart = ({ data, title, dataKey, valueKey, color = '#1976d2' }) => {
    if (!data || data.length === 0) {
        return (
            <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>{title}</Typography>
                <Typography color="text.secondary">No data available</Typography>
            </Paper>
        );
    }

    const maxValue = Math.max(...data.map(item => item[valueKey] || 0));

    return (
        <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>{title}</Typography>
            <Box sx={{ mt: 2 }}>
                {data.map((item, index) => {
                    const value = item[valueKey] || 0;
                    const percentage = maxValue > 0 ? (value / maxValue) * 100 : 0;
                    
                    return (
                        <Box key={index} sx={{ mb: 2 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                                <Typography variant="body2" color="text.secondary">
                                    {item[dataKey]}
                                </Typography>
                                <Typography variant="body2" fontWeight="bold">
                                    {value}
                                </Typography>
                            </Box>
                            <Box
                                sx={{
                                    width: '100%',
                                    height: 8,
                                    backgroundColor: '#e0e0e0',
                                    borderRadius: 1,
                                    overflow: 'hidden'
                                }}
                            >
                                <Box
                                    sx={{
                                        width: `${percentage}%`,
                                        height: '100%',
                                        backgroundColor: color,
                                        transition: 'width 0.3s ease'
                                    }}
                                />
                            </Box>
                        </Box>
                    );
                })}
            </Box>
        </Paper>
    );
};

export default BarChart;
