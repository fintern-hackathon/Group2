import { useThemeColor } from '@/hooks/useThemeColor';
import { Image } from 'expo-image';
import React from 'react';
import { StyleSheet, View } from 'react-native';
import Svg, { Path } from 'react-native-svg';
import { ThemedText } from './ThemedText';

interface TreeProgressProps {
  financialScore: number; // 0-1000 financial score
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
  const primaryColor = useThemeColor({}, 'primary');
  const secondaryColor = useThemeColor({}, 'secondary');
  
  const radius = (size - strokeWidth) / 2;
  const center = size / 2;
  const treeSize = size * 0.5; // Tree size relative to circle - increased

  // Convert financial score (0-1000) to progress (0-100)
  const progress = Math.min((financialScore / 1000) * 100, 100);
  
  // Calculate 270-degree arc (from -135° to +135°) - gap centered below tree
  const startAngle = -135; // Start at -135 degrees (top-left)
  const endAngle = 135;    // End at +135 degrees (top-right)
  const totalAngle = 270;  // Total arc is 270 degrees
  
  // Calculate the current angle based on progress
  const currentAngle = startAngle + (progress / 100) * totalAngle;
  
  // Convert angles to radians
  const startRad = (startAngle * Math.PI) / 180;
  const currentRad = (currentAngle * Math.PI) / 180;
  
  // Calculate arc path
  const x1 = center + radius * Math.cos(startRad);
  const y1 = center + radius * Math.sin(startRad);
  const x2 = center + radius * Math.cos(currentRad);
  const y2 = center + radius * Math.sin(currentRad);
  
  // Determine if we need to draw a large arc (more than 180 degrees)
  const largeArcFlag = progress > 50 ? 1 : 0;
  
  // Create the arc path
  const arcPath = progress > 0 ? 
    `M ${x1} ${y1} A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}` : 
    '';

  // Get tree image based on financial score
  const getTreeImage = (score: number) => {
    if (score >= 800) {
      return require('@/assets/images/tree6.png'); // Mükemmel - en büyük ağaç
    } else if (score >= 600) {
      return require('@/assets/images/tree5.png'); // İyi - büyük ağaç
    } else if (score >= 400) {
      return require('@/assets/images/tree3.png'); // Orta - orta ağaç
    } else {
      return require('@/assets/images/tree1.png'); // Geliştirilmeli - küçük ağaç
    }
  };

  // Calculate score display
  const displayScore = Math.round(financialScore);

  return (
    <View style={styles.container}>
      <Svg width={size} height={size} style={styles.svg}>
        {/* Background circle (270 degrees) */}
        <Path
          d={`M ${center + radius * Math.cos(startRad)} ${center + radius * Math.sin(startRad)} A ${radius} ${radius} 0 1 1 ${center + radius * Math.cos(endAngle * Math.PI / 180)} ${center + radius * Math.sin(endAngle * Math.PI / 180)}`}
          stroke={secondaryColor}
          strokeWidth={strokeWidth}
          fill="transparent"
          opacity={0.16}
        />
        
        {/* Progress arc */}
        {progress > 0 && (
          <Path
            d={arcPath}
            stroke={secondaryColor}
            strokeWidth={strokeWidth}
            fill="transparent"
            strokeLinecap="round"
          />
        )}
      </Svg>
      
      {/* Tree Image */}
      <View style={[styles.treeContainer, { width: treeSize, height: treeSize }]}>
        <Image
          source={getTreeImage(financialScore)}
          style={styles.treeImage}
          contentFit="contain"
        />
      </View>
      
      {/* Financial Score Display - moved below tree and progress bar */}
      {showScore && (
        <View style={styles.scoreContainer}>
          <ThemedText style={styles.scoreText}>
            {displayScore}
          </ThemedText>
          <ThemedText style={styles.scoreLabel}>
            Finansal Skor
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
    bottom: -80,
    alignItems: 'center',
  },
  scoreText: {
    fontSize: 32,
    fontWeight: '700',
    color: '#0057B8', // Blue color
    marginBottom: 4,
  },
  scoreLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#0057B8', // Blue color
    opacity: 0.8,
  },
}); 