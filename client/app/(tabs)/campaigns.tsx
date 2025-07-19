import React, { useState } from 'react';
import { Alert, ScrollView, StyleSheet, TouchableOpacity, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { BottomNavigation } from '@/components/BottomNavigation';
import { ProfileHeader } from '@/components/ProfileHeader';
import { TopBar } from '@/components/TopBar';
import { TreeProgress } from '@/components/TreeProgress';
import { useThemeColor } from '@/hooks/useThemeColor';

export default function CampaignsScreen() {
  const [activeTab, setActiveTab] = useState('campaigns');
  const [financialScore, setFinancialScore] = useState(750);
  
  const backgroundColor = useThemeColor({}, 'background');

  const tabs = [
    { id: 'home', label: 'Ana Sayfa', icon: '🏠', isActive: activeTab === 'home' },
    { id: 'transactions', label: 'İşlemler', icon: '☰', isActive: activeTab === 'transactions' },
    { id: 'assets', label: 'Varlıklar/Borçlar', icon: '🔄', isActive: activeTab === 'assets' },
    { id: 'campaigns', label: 'Kampanyalar', icon: '🎁', isActive: activeTab === 'campaigns' },
  ];

  const handleTabPress = (tabId: string) => {
    setActiveTab(tabId);
    if (tabId === 'home') {
      Alert.alert('Ana Sayfa', 'Ana sayfaya yönlendiriliyorsunuz...');
    }
  };

  const handleScoreChange = () => {
    // Finansal skoru rastgele değiştir (0-1000 arası)
    setFinancialScore(Math.floor(Math.random() * 1000) + 1);
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor }]} edges={['top']}>
      <TopBar title="FinTree" showBackButton={true} />
      
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Profile Header */}
        <ProfileHeader userName="Alican" greeting="İyi günler," />
        
        {/* Progress Section with Tree */}
        <View style={styles.progressSection}>
          <TouchableOpacity onPress={handleScoreChange} style={styles.treeButton}>
            <TreeProgress 
              financialScore={financialScore} 
              size={320}
            />
          </TouchableOpacity>
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
  progressSection: {
    alignItems: 'center',
    paddingVertical: 60,
  },
  treeButton: {
    alignItems: 'center',
  },
}); 