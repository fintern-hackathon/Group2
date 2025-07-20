import { useThemeColor } from '@/hooks/useThemeColor';
import React from 'react';
import { StyleSheet, TouchableOpacity, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { ThemedText } from './ThemedText';

interface TabItem {
  id: string;
  label: string;
  icon: string;
  isActive?: boolean;
}

interface BottomNavigationProps {
  tabs: TabItem[];
  onTabPress: (tabId: string) => void;
}

export function BottomNavigation({ tabs, onTabPress }: BottomNavigationProps) {
  const backgroundColor = useThemeColor({}, 'white');
  const borderColor = useThemeColor({}, 'border');
  const activeColor = useThemeColor({}, 'primary');
  const inactiveColor = useThemeColor({}, 'lightGray');
  const insets = useSafeAreaInsets();

  return (
    <View style={[
      styles.container, 
      { 
        backgroundColor, 
        borderTopColor: borderColor,
        paddingBottom: insets.bottom 
      }
    ]}>
      {tabs.map((tab) => (
        <TouchableOpacity
          key={tab.id}
          style={styles.tab}
          onPress={() => onTabPress(tab.id)}
          activeOpacity={0.7}
        >
          <View style={styles.iconContainer}>
            <ThemedText style={[
              styles.icon, 
              { color: tab.isActive ? activeColor : inactiveColor }
            ]}>
              {tab.icon}
            </ThemedText>
          </View>
          <ThemedText style={[
            styles.label, 
            { color: tab.isActive ? activeColor : inactiveColor }
          ]}>
            {tab.label}
          </ThemedText>
        </TouchableOpacity>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    borderTopWidth: 1,
    paddingTop: 12,
  },
  tab: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 8,
  },
  iconContainer: {
    width: 20,
    height: 20,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 4,
  },
  icon: {
    fontSize: 18,
  },
  label: {
    fontSize: 11,
    fontWeight: '400',
    lineHeight: 14,
  },
}); 