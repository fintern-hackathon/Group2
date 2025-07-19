import { Image } from 'expo-image';
import React from 'react';
import { StyleSheet, View } from 'react-native';
import Svg, { Path } from 'react-native-svg';
import { ThemedText } from './ThemedText';

interface TreeProgressProps {
  financialScore: number; // 0-1000
  size?: number;
  strokeWidth?: number;
  showScore?: boolean;
}

export function TreeProgress({
  financialScore,
  size = 320,
  strokeWidth = 16,
  showScore = true
}: TreeProgressProps) {
  const center = size / 2;
  const radius = (size - strokeWidth) / 2;
  const treeSize = size * 0.5;

  const progress = Math.min((financialScore / 1000) * 100, 100);
  
  // Calculate 270-degree arc (from +135° to +405°) - gap centered at bottom
  const startAngle = 135;  // Start at +135 degrees (top-left)
  const endAngle = 405;    // End at +405 degrees (bottom-right)
  const totalAngle = 270;  // Total arc is 270 degrees
  
  // Calculate the current angle based on progress
  const currentAngle = startAngle + (progress / 100) * totalAngle;

  const startRad = (startAngle * Math.PI) / 180;
  const currentRad = (currentAngle * Math.PI) / 180;

  const x1 = center + radius * Math.cos(startRad);
  const y1 = center + radius * Math.sin(startRad);
  const x2 = center + radius * Math.cos(currentRad);
  const y2 = center + radius * Math.sin(currentRad);

  // Create a more rounded arc path
  const arcPath = progress > 0
    ? `M ${x1} ${y1} A ${radius} ${radius} 0 ${progress > 50 ? 1 : 0} 1 ${x2} ${y2}`
    : '';

  const displayScore = `%${Math.round(progress)}`;

  const getTreeImage = (score: number) => {
    if (score >= 800) return require('@/assets/images/tree6.png');
    if (score >= 600) return require('@/assets/images/tree5.png');
    if (score >= 400) return require('@/assets/images/tree3.png');
    return require('@/assets/images/tree1.png');
  };

  return (
    <View style={styles.container}>
      <Svg width={size} height={size} style={styles.svg}>
        {/* Background arc */}
        <Path
          d={`M ${center + radius * Math.cos(startRad)} ${center + radius * Math.sin(startRad)} A ${radius} ${radius} 0 1 1 ${center + radius * Math.cos(endAngle * Math.PI / 180)} ${center + radius * Math.sin(endAngle * Math.PI / 180)}`}
          stroke="#CDE8A3"
          strokeWidth={strokeWidth}
          fill="transparent"
          opacity={1}
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Foreground arc */}
        {progress > 0 && (
          <Path
            d={arcPath}
            stroke="#86C443"
            strokeWidth={strokeWidth}
            fill="transparent"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        )}
      </Svg>

      {/* Tree image */}
      <View style={[styles.treeContainer, { width: treeSize, height: treeSize }]}>
        <Image
          source={getTreeImage(financialScore)}
          style={styles.treeImage}
          contentFit="contain"
        />
      </View>

      {/* Score */}
      {showScore && (
        <View style={styles.scoreContainer}>
          <ThemedText style={styles.scoreText}>{displayScore}</ThemedText>
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
  treeContainer: {
    position: 'absolute',
    alignItems: 'center',
    justifyContent: 'center',
  },
  treeImage: {
    width: '100%',
    height: '100%',
  },
  scoreContainer: {
    position: 'absolute',
    bottom: -60,
    alignItems: 'center',
  },
  scoreText: {
    fontSize: 24,
    fontWeight: '700',
    color: '#0057B8',
  },
});
