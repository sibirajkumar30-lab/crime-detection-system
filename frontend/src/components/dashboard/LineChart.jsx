import React from 'react';
import { Box, Paper, Typography } from '@mui/material';

const LineChart = ({ data, title, xKey, yKey, color = '#1976d2' }) => {
    if (!data || data.length === 0) {
        return (
            <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>{title}</Typography>
                <Typography color="text.secondary">No data available</Typography>
            </Paper>
        );
    }

    const maxValue = Math.max(...data.map(item => item[yKey] || 0), 1);
    const chartHeight = 200;

    return (
        <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>{title}</Typography>
            <Box sx={{ position: 'relative', height: chartHeight, mt: 2, mb: 4 }}>
                {/* Y-axis labels */}
                <Box sx={{ position: 'absolute', left: -40, top: 0, bottom: 20, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                    <Typography variant="caption" color="text.secondary">{maxValue}</Typography>
                    <Typography variant="caption" color="text.secondary">{Math.round(maxValue / 2)}</Typography>
                    <Typography variant="caption" color="text.secondary">0</Typography>
                </Box>

                {/* Chart area */}
                <Box sx={{ position: 'relative', height: '100%', display: 'flex', alignItems: 'flex-end', gap: 1 }}>
                    {data.map((item, index) => {
                        const value = item[yKey] || 0;
                        const heightPercentage = (value / maxValue) * 100;
                        
                        return (
                            <Box
                                key={index}
                                sx={{
                                    flex: 1,
                                    display: 'flex',
                                    flexDirection: 'column',
                                    alignItems: 'center'
                                }}
                            >
                                <Box
                                    sx={{
                                        width: '100%',
                                        height: `${heightPercentage}%`,
                                        backgroundColor: color,
                                        borderRadius: '4px 4px 0 0',
                                        transition: 'height 0.3s ease',
                                        minHeight: value > 0 ? '4px' : '0',
                                        position: 'relative',
                                        '&:hover': {
                                            opacity: 0.8
                                        }
                                    }}
                                >
                                    <Typography
                                        variant="caption"
                                        sx={{
                                            position: 'absolute',
                                            top: -20,
                                            left: '50%',
                                            transform: 'translateX(-50%)',
                                            fontWeight: 'bold'
                                        }}
                                    >
                                        {value}
                                    </Typography>
                                </Box>
                            </Box>
                        );
                    })}
                </Box>
            </Box>

            {/* X-axis labels */}
            <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                {data.map((item, index) => (
                    <Box key={index} sx={{ flex: 1, textAlign: 'center' }}>
                        <Typography variant="caption" color="text.secondary" noWrap>
                            {item[xKey]}
                        </Typography>
                    </Box>
                ))}
            </Box>
        </Paper>
    );
};

export default LineChart;
