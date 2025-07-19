import { useThemeColor } from '@/hooks/useThemeColor';
import React from 'react';
import { StyleSheet, View } from 'react-native';
import Svg, { Circle } from 'react-native-svg';
import { ThemedText } from './ThemedText';

interface CircularProgressProps {
  progress: number; // 0-100
  size?: number;
  strokeWidth?: number;
  showPercentage?: boolean;
}

export function CircularProgress({ 
  progress, 
  size = 319, 
  strokeWidth = 8,
  showPercentage = true 
}: CircularProgressProps) {
  const primaryColor = useThemeColor({}, 'primary');
  const secondaryColor = useThemeColor({}, 'secondary');
  const textColor = useThemeColor({}, 'text');
  
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDashoffset = circumference - (progress / 100) * circumference;
  
  const center = size / 2;

  return (
    <View style={styles.container}>
      <Svg width={size} height={size} style={styles.svg}>
        {/* Background circle */}
        <Circle
          cx={center}
          cy={center}
          r={radius}
          stroke={secondaryColor}
          strokeWidth={strokeWidth}
          fill="transparent"
          opacity={0.16}
        />
        {/* Progress circle */}
        <Circle
          cx={center}
          cy={center}
          r={radius}
          stroke={secondaryColor}
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          transform={`rotate(-90 ${center} ${center})`}
        />
      </Svg>
      
      {showPercentage && (
        <View style={styles.percentageContainer}>
          <ThemedText style={[styles.percentage, { color: primaryColor }]}>
            %{progress}
          </ThemedText>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  svg: {
    position: 'absolute',
  },
  percentageContainer: {
    position: 'absolute',
    alignItems: 'center',
    justifyContent: 'center',
  },
  percentage: {
    fontSize: 24,
    fontWeight: '700',
    lineHeight: 30,
  },
}); 