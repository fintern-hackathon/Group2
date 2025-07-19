import React from 'react';
import { ScrollView, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { ProfileHeader } from '@/components/ProfileHeader';
import { ThemedText } from '@/components/ThemedText';
import { TopBar } from '@/components/TopBar';
import { useThemeColor } from '@/hooks/useThemeColor';

export default function HomeScreen() {
  const backgroundColor = useThemeColor({}, 'background');
  const textColor = useThemeColor({}, 'text');

  return (
    <SafeAreaView style={[styles.container, { backgroundColor }]} edges={['top']}>
      <TopBar title="Ana Sayfa" />
      
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Profile Header */}
        <ProfileHeader userName="Alican" greeting="İyi günler 👋" />
        
        {/* Welcome Section */}
        <View style={styles.welcomeSection}>
          <ThemedText style={[styles.welcomeTitle, { color: textColor }]}>
            Hoş Geldiniz!
          </ThemedText>
          <ThemedText style={[styles.welcomeText, { color: textColor }]}>
            Bankacılık işlemlerinizi kolayca gerçekleştirin.
          </ThemedText>
        </View>
        
        {/* Quick Actions */}
        <View style={styles.quickActionsSection}>
          <ThemedText style={[styles.sectionTitle, { color: textColor }]}>
            Hızlı İşlemler
          </ThemedText>
          <View style={styles.actionsGrid}>
            <View style={styles.actionItem}>
              <ThemedText style={styles.actionIcon}>💳</ThemedText>
              <ThemedText style={[styles.actionText, { color: textColor }]}>
                Kartlarım
              </ThemedText>
            </View>
            <View style={styles.actionItem}>
              <ThemedText style={styles.actionIcon}>💰</ThemedText>
              <ThemedText style={[styles.actionText, { color: textColor }]}>
                Para Transferi
              </ThemedText>
            </View>
            <View style={styles.actionItem}>
              <ThemedText style={styles.actionIcon}>📊</ThemedText>
              <ThemedText style={[styles.actionText, { color: textColor }]}>
                Yatırım
              </ThemedText>
            </View>
            <View style={styles.actionItem}>
              <ThemedText style={styles.actionIcon}>🎯</ThemedText>
              <ThemedText style={[styles.actionText, { color: textColor }]}>
                Kampanyalar
              </ThemedText>
            </View>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  welcomeSection: {
    paddingHorizontal: 16,
    paddingVertical: 20,
  },
  welcomeTitle: {
    fontSize: 24,
    fontWeight: '700',
    lineHeight: 32,
    marginBottom: 8,
  },
  welcomeText: {
    fontSize: 16,
    fontWeight: '400',
    lineHeight: 24,
    opacity: 0.8,
  },
  quickActionsSection: {
    paddingHorizontal: 16,
    paddingVertical: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    lineHeight: 24,
    marginBottom: 16,
  },
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  actionItem: {
    width: '48%',
    alignItems: 'center',
    paddingVertical: 20,
    marginBottom: 16,
    borderRadius: 12,
    backgroundColor: 'rgba(0, 87, 184, 0.05)',
  },
  actionIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  actionText: {
    fontSize: 14,
    fontWeight: '600',
    lineHeight: 18,
  },
});
