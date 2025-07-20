import React, { useState } from 'react';
import { Alert, ScrollView, StyleSheet, TouchableOpacity, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { BottomNavigation } from '@/components/BottomNavigation';
import { CampaignCard } from '@/components/CampaignCard';
import { ProfileHeader } from '@/components/ProfileHeader';
import { TopBar } from '@/components/TopBar';
import { TreeProgress } from '@/components/TreeProgress';
import { useThemeColor } from '@/hooks/useThemeColor';

export default function CampaignsScreen() {
  const [activeTab, setActiveTab] = useState('campaigns');
  const [financialScore, setFinancialScore] = useState(75);

  const backgroundColor = useThemeColor({}, 'background');

  const tabs = [
    { id: 'campaigns', label: 'Kampanyalar', icon: '🎁', isActive: activeTab === 'campaigns' },
    { id: 'profile', label: 'Profil', icon: '👤', isActive: activeTab === 'profile' },
  ];

  const handleTabPress = (tabId: string) => {
    setActiveTab(tabId);
    if (tabId === 'profile') {
      Alert.alert('Profil', 'Profil sayfasına yönlendiriliyorsunuz...');
    }
  };

  const handleScoreChange = () => {
    setFinancialScore(Math.floor(Math.random() * 1000) + 1);
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor }]} edges={[]}>
      <TopBar title="" />

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
        {/* Profile Header - Top */}
        <View style={styles.profileSection}>
          <ProfileHeader userName="Alican" greeting="İyi günler," />
        </View>

        {/* Tree Progress - Center */}
        <View style={styles.progressSection}>
          <TouchableOpacity onPress={handleScoreChange} style={styles.treeButton}>
            <TreeProgress financialScore={financialScore} size={320} />
          </TouchableOpacity>
        </View>

        {/* Campaign Card - Bottom */}
        <View style={styles.campaignSection}>
          <CampaignCard
            onCancel={() => Alert.alert('Geri', 'info')}
            onConfirm={() => Alert.alert('Tamam', 'info')}
          />
        </View>
      </ScrollView>

      <BottomNavigation tabs={tabs} onTabPress={handleTabPress} />
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
  scrollContent: {
    flexGrow: 1,
  },
  progressSection: {
    alignItems: 'center',
    flex: 1,
    justifyContent: 'center',
  },
  treeButton: {
    alignItems: 'center',
  },
  profileSection: {
    paddingHorizontal: 16,
    paddingBottom: 20,
  },
  campaignSection: {
    paddingHorizontal: 16,
    paddingBottom: 20,
  },
});
