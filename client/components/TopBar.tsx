import { useThemeColor } from '@/hooks/useThemeColor';
import React from 'react';
import { StatusBar, StyleSheet, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { ThemedText } from './ThemedText';

interface TopBarProps {
  title?: string;
  showBackButton?: boolean;
  onBackPress?: () => void;
  rightComponent?: React.ReactNode;
}

export function TopBar({ 
  title = 'Kampanyalar', 
  showBackButton = false,
  onBackPress,
  rightComponent 
}: TopBarProps) {
  const primaryColor = useThemeColor({}, 'primary');
  const textColor = useThemeColor({}, 'white');
  const insets = useSafeAreaInsets();

  return (
    <View style={[styles.container, { backgroundColor: primaryColor, paddingTop: insets.top }]}>
      <StatusBar barStyle="light-content" backgroundColor={primaryColor} />
      <View style={styles.content}>
        <View style={styles.leftSection}>
          {showBackButton && (
            <ThemedText style={[styles.backButton, { color: textColor }]} onPress={onBackPress}>
              ←
            </ThemedText>
          )}
        </View>
        
        <View style={styles.centerSection}>
          <ThemedText style={[styles.title, { color: textColor }]}>
            {title}
          </ThemedText>
        </View>
        
        <View style={styles.rightSection}>
          {rightComponent}
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: '100%',
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    minHeight: 46,
  },
  leftSection: {
    flex: 1,
    alignItems: 'flex-start',
  },
  centerSection: {
    flex: 2,
    alignItems: 'center',
  },
  rightSection: {
    flex: 1,
    alignItems: 'flex-end',
  },
  title: {
    fontSize: 14,
    fontWeight: '700',
    lineHeight: 18,
  },
  backButton: {
    fontSize: 18,
    fontWeight: '600',
  },
}); 