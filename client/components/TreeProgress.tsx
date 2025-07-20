import { Image } from 'expo-image';
import React from 'react';
import { StyleSheet, View } from 'react-native';
import Svg, { Circle, Path, Line, Text as SvgText } from 'react-native-svg';
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
  const treeSize = size * 0.6;

  const progress = Math.min(financialScore, 100);
  
  // Calculate 270-degree arc (from +135° to +405°) - gap centered at bottom
  const startAngle = 135;  // Start at +135 degrees (top-left)
  const endAngle = 405;    // End at +405 degrees (bottom-right)
  const totalAngle = 270;  // Total arc is 270 degrees
  
  // Calculate the current angle based on progress
  const currentAngle = startAngle + (progress / 100) * totalAngle;
  
  // Convert angles to radians
  const startRad = (startAngle * Math.PI) / 180;
  const currentRad = (currentAngle * Math.PI) / 180;
  
  // Calculate dot position
  const dotX = center + radius * Math.cos(currentRad);
  const dotY = center + radius * Math.sin(currentRad);

  const displayScore = `%${Math.round(progress)}`;

  const getTreeImage = (score: number) => {
    if (score >= 80) return require('@/assets/images/tree6.png');
    if (score >= 60) return require('@/assets/images/tree5.png');
    if (score >= 40) return require('@/assets/images/tree4.png');
    if (score >= 20) return require('@/assets/images/tree3.png');
    return require('@/assets/images/tree1.png');
  };

  // Arka yay rengi: %40 ve altı için saydam kırmızı, üstü için saydam yeşil
  const backgroundArcColor = progress <= 40 ? 'rgba(229,57,53,0.18)' : 'rgba(134,196,67,0.18)';
  const progressColor = progress <= 40 ? '#E53935' : '#86C443';

  // %0 ve %100 yazılarının pozisyonu (baş ve son noktalar)
  const percentLabelOffset = 28; // yaydan biraz dışarıda dursun
  const percent0X = center + (radius + percentLabelOffset) * Math.cos(startRad);
  const percent0Y = center + (radius + percentLabelOffset) * Math.sin(startRad);
  const percent100X = center + (radius + percentLabelOffset) * Math.cos((endAngle * Math.PI) / 180);
  const percent100Y = center + (radius + percentLabelOffset) * Math.sin((endAngle * Math.PI) / 180);

  return (
    <View style={styles.container}>
      <Svg width={size} height={size} style={styles.svg}>
        {/* Background arc - skora göre renkli */}
        <Path
          d={`M ${center + radius * Math.cos(startRad)} ${center + radius * Math.sin(startRad)} A ${radius} ${radius} 0 1 1 ${center + radius * Math.cos(endAngle * Math.PI / 180)} ${center + radius * Math.sin(endAngle * Math.PI / 180)}`}
          stroke={backgroundArcColor}
          strokeWidth={strokeWidth}
          fill="transparent"
          opacity={1}
          strokeLinecap="round"
        />

        {/* Progress dot - sadece uçta yuvarlak */}
        {progress > 0 && (
          <Circle
            cx={dotX}
            cy={dotY}
            r={strokeWidth / 2}
            fill={progressColor}
          />
        )}

        {/* %0 ve %100 yazıları */}
        <SvgText
          x={percent0X}
          y={percent0Y + 8}
          fontSize={18}
          fontWeight="bold"
          fill="#B0B0B0"
          textAnchor="middle"
        >
          %0
        </SvgText>
        <SvgText
          x={percent100X}
          y={percent100Y + 8}
          fontSize={18}
          fontWeight="bold"
          fill="#B0B0B0"
          textAnchor="middle"
        >
          %100
        </SvgText>
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
  },
  treeContainer: {
    position: 'absolute',
    alignItems: 'center',
    justifyContent: 'center',
  },
  treeImage: {
    width: '110%',
    borderRadius: 100,
    height: '110%',
  },
  scoreContainer: {
    position: 'absolute',
    bottom: -20,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
  },
  scoreText: {
    fontSize: 32,
    fontWeight: '700',
    color: '#0057B8',
    textAlign: 'center',
    lineHeight: 40,
  },
});
