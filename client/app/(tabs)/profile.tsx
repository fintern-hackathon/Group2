import React from 'react';
import { StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { ThemedText } from '@/components/ThemedText';
import { TopBar } from '@/components/TopBar';
import { useThemeColor } from '@/hooks/useThemeColor';

export default function ProfileScreen() {
  const backgroundColor = useThemeColor({}, 'background');

  return (
    <SafeAreaView style={[styles.container, { backgroundColor }]} edges={['top']}>
      <TopBar title="Profil" />
      
      <View style={styles.content}>
        <ThemedText style={styles.title}>Profil Sayfası</ThemedText>
        <ThemedText style={styles.subtitle}>Bu sayfa geliştirme aşamasında...</ThemedText>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    marginBottom: 12,
  },
  subtitle: {
    fontSize: 16,
    opacity: 0.7,
  },
}); 