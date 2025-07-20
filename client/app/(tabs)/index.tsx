import React, { useState, useEffect } from 'react';
import { Alert, ScrollView, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { BottomNavigation } from '@/components/BottomNavigation';
import { CampaignCard } from '@/components/CampaignCard';
import { ProfileHeader } from '@/components/ProfileHeader';
import { TopBar } from '@/components/TopBar';
import { TreeProgress } from '@/components/TreeProgress';
import { useThemeColor } from '@/hooks/useThemeColor';

export default function IndexScreen() {
  const [activeTab, setActiveTab] = useState('campaigns');
  const [financialScore, setFinancialScore] = useState(75); // Varsayılan skor
  const [suggestion, setSuggestion] = useState('');

  // Skoru backend'den çek
  useEffect(() => {
    const fetchScore = async () => {
      try {
        const response = await fetch('http://localhost:8004/api/v1/analytics/1/score');
        if (!response.ok) throw new Error('API error');
        const data = await response.json();
        console.log('API response:', data);
        if (typeof data.total_score !== 'number' || isNaN(data.total_score)) {
          console.warn('API skoru geçersiz:', data.total_score);
        }
        setFinancialScore(data.total_score);
      } catch (error) {
        console.error('Skor alınamadı:', error);
      }
    };
    fetchScore();
  }, []);

  // Daily suggestion'ı backend'den çek
  useEffect(() => {
    const fetchSuggestion = async () => {
      try {
        const response = await fetch('http://localhost:8004/api/v1/mcp-client/daily-suggestion', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: '7f3c989b-221e-47c3-b502-903199b39ad4' })
        });
        if (!response.ok) throw new Error('API error');
        const data = await response.json();
        console.log('Daily suggestion response:', data);
        // Varsayılan anahtar suggestion, yoksa logdan bakılır
        setSuggestion(data.suggestion || '');
      } catch (error) {
        console.error('Daily suggestion alınamadı:', error);
      }
    };
    fetchSuggestion();
  }, []);

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

  return (
    <SafeAreaView style={[styles.container, { backgroundColor }]} edges={[]}>
      <TopBar title="FinTree" />

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
        {/* Profile Header - Top */}
        <View style={styles.profileSection}>
          <ProfileHeader userName="Alican" greeting="İyi günler," />
        </View>

        {/* Tree Progress - Center */}
        <View style={styles.progressSection}>
          <TreeProgress financialScore={financialScore} size={320} />
        </View>

        {/* Campaign Card - Bottom */}
        <View style={styles.campaignSection}>
          <CampaignCard
            onCancel={() => Alert.alert('Geri', 'info')}
            onConfirm={() => Alert.alert('Tamam', 'info')}
            description={suggestion || 'Öneri yükleniyor...'}
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
  profileSection: {
    paddingBottom: 20,
  },
  campaignSection: {
    paddingHorizontal: 16,
    paddingBottom: 20,
  },
}); 