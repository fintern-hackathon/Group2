import { useThemeColor } from '@/hooks/useThemeColor';
import React from 'react';
import { StatusBar, StyleSheet, TouchableOpacity, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ThemedText } from './ThemedText';

interface TopBarProps {
  title: string;
  showBackButton?: boolean;
  onBackPress?: () => void;
}

export function TopBar({ title, showBackButton = false, onBackPress }: TopBarProps) {
  const primaryColor = useThemeColor({}, 'primary');

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: primaryColor }]} edges={[]}>
      <StatusBar barStyle="light-content" backgroundColor={primaryColor} />
      
      {/* Dynamic Island area - invisible spacer */}
      <View style={styles.dynamicIslandSpace} />
      
      {/* Title bar */}
      <View style={[styles.titleBar, { backgroundColor: primaryColor }]}>
        {showBackButton && (
          <TouchableOpacity onPress={onBackPress} style={styles.backButton}>
            <ThemedText style={styles.backButtonText}>←</ThemedText>
          </TouchableOpacity>
        )}
        {title && <ThemedText style={styles.title}>{title}</ThemedText>}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    width: '100%',
  },
  dynamicIslandSpace: {
    height: 50, // Dynamic Island alanı için boşluk
  },
  titleBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    minHeight: 44,
  },
  backButton: {
    position: 'absolute',
    left: 16,
    zIndex: 1,
  },
  backButtonText: {
    fontSize: 20,
    color: 'white',
    fontWeight: '600',
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: 'white',
  },
}); 