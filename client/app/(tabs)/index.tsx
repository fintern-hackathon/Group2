import React, { useEffect, useState } from 'react';
import { ActivityIndicator, Alert, Modal, Pressable, ScrollView, StyleSheet, TouchableOpacity, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { BottomNavigation } from '@/components/BottomNavigation';
import { CampaignCard } from '@/components/CampaignCard';
import { Collapsible } from '@/components/Collapsible';
import { ProfileHeader } from '@/components/ProfileHeader';
import { ThemedText } from '@/components/ThemedText';
import { TopBar } from '@/components/TopBar';
import { TreeProgress } from '@/components/TreeProgress';
import { IconSymbol } from '@/components/ui/IconSymbol';
import { useThemeColor } from '@/hooks/useThemeColor';
import MaterialIcons from '@expo/vector-icons/MaterialIcons';

export default function IndexScreen() {
  const [activeTab, setActiveTab] = useState('campaigns');
  const [financialScore, setFinancialScore] = useState(75); // Varsayılan skor
  const [suggestion, setSuggestion] = useState('');
  const [personalityName, setPersonalityName] = useState('Savurgan'); // Default value
  const [personalityDescription, setPersonalityDescription] = useState(''); // Personality description
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [loading, setLoading] = useState(false);

  // Personality descriptions
  const personalityDescriptions = {
    'cesur_aslan': 'Risk alır, büyük harcamalar, hedef odaklı',
    'caliskan_sincap': 'Çok tasarruf eden ama keyif almayı unutan',
    'ozgur_kelebegi': 'Spontan, keyifli, anlık kararlar',
    'sabit_kaplumbaga': 'Tutarlı, güvenli, değişim sevmeyen',
    'konfor_koala': 'Konfor odaklı, rahat yaşam',
    'akilli_baykus': 'Planlı, uzun vadeli düşünen'
  };

  // Skoru backend'den çek
  const fetchScore = async () => {
    try {
      const response = await fetch('http://192.168.1.16:8006/api/v1/analytics/866a6327-773a-4777-a60a-cf45b90f0851/score');
      if (!response.ok) throw new Error('API error');
      const data = await response.json();
      console.log('Score API response:', data);
      if (typeof data.total_score !== 'number' || isNaN(data.total_score)) {
        console.warn('API skoru geçersiz:', data.total_score);
        setFinancialScore(75); // Fallback değer
      } else {
        setFinancialScore(data.total_score);
        console.log('Financial score set to:', data.total_score);
      }
    } catch (error) {
      console.error('Skor alınamadı:', error);
      setFinancialScore(75); // Fallback değer
    }
  };
  useEffect(() => {
    fetchScore();
  }, []);

  // Daily suggestion'ı backend'den çek
  const fetchSuggestion = async () => {
    try {
      const response = await fetch('http://192.168.1.16:8006/api/v1/mcp-client/daily-suggestion', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: '866a6327-773a-4777-a60a-cf45b90f0851' })
      });
      if (!response.ok) throw new Error('API error');
      const data = await response.json();
      console.log('Daily suggestion response:', data);
      console.log('suggestion_text value:', data.suggestion_text);
      console.log('suggestion value:', data.suggestion);
      console.log('suggestion_text type:', typeof data.suggestion_text);
      console.log('suggestion type:', typeof data.suggestion);
      
      // Try both fields for compatibility
      const suggestionValue = data.suggestion_text || data.suggestion || '';
      setSuggestion(suggestionValue);
      console.log('State suggestion set to:', suggestionValue);
    } catch (error) {
      console.error('Daily suggestion alınamadı:', error);
    }
  };
  // Personality verisini backend'den çek
  const fetchPersonality = async () => {
    try {
      const response = await fetch('http://192.168.1.16:8006/api/v1/personality/866a6327-773a-4777-a60a-cf45b90f0851');
      if (!response.ok) throw new Error('API error');
      const data = await response.json();
      console.log('Personality response:', data);
      if (data.success && data.data && data.data.personality_name) {
        // Emoji mapping for broken characters
        let personalityName = data.data.personality_name;
        
        // Use personality type to get correct emoji and name
        const personalityType = data.data.personality_type;
        const personalityMap = {
          'cesur_aslan': { emoji: '🦁', name: 'Cesur Aslan' },
          'caliskan_sincap': { emoji: '🐿️', name: 'Çalışkan Sincap' },
          'ozgur_kelebegi': { emoji: '🦋', name: 'Özgür Kelebek' },
          'sabit_kaplumbaga': { emoji: '🐢', name: 'Sabit Kaplumbağa' },
          'konfor_koala': { emoji: '🐨', name: 'Konfor Koala' },
          'akilli_baykus': { emoji: '🦉', name: 'Akıllı Baykuş' }
        };
        
        // Get personality info from type
        const personalityInfo = personalityMap[personalityType as keyof typeof personalityMap] || { emoji: '🦁', name: 'Cesur Aslan' };
        
        // Use clean emoji and name
        personalityName = `${personalityInfo.emoji} ${personalityInfo.name}`;
        
        // Set personality description
        const description = personalityDescriptions[personalityType as keyof typeof personalityDescriptions] || 'Risk alır, büyük harcamalar, hedef odaklı';
        
        setPersonalityName(personalityName);
        setPersonalityDescription(description);
        console.log('Personality name set to:', personalityName);
        console.log('Personality description set to:', description);
      }
    } catch (error) {
      console.error('Personality alınamadı:', error);
    }
  };

  useEffect(() => {
    fetchPersonality();
  }, []);

  useEffect(() => {
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

  const handleRefresh = async () => {
    setIsRefreshing(true);
    setLoading(true);
    await Promise.all([
      fetchScore(),
      fetchSuggestion(),
      fetchPersonality()
    ]);
    setIsRefreshing(false);
    setLoading(false);
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor }]} edges={[]}>
      <TopBar title="FinTree" />

      {/* Loading Modal */}
      <Modal visible={loading} transparent animationType="fade">
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#0057B8" />
        </View>
      </Modal>



      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent} scrollEnabled={!loading}>
        {/* Profile Header + Refresh Button + Badge */}
        <View style={styles.profileRowWrap}>
          <View style={{ flex: 1 }}>
            <ProfileHeader userName="Alican" greeting="İyi günler," />
          </View>
          <TouchableOpacity
            style={styles.refreshButton}
            onPress={handleRefresh}
            disabled={loading}
          >
            <MaterialIcons name="sync" size={22} color="#0057B8" />
          </TouchableOpacity>
        </View>
        <View style={styles.badgeWrap}>
          <Collapsible title={personalityName}>
            <ThemedText style={styles.personalityDescription}>
              {personalityDescription}
            </ThemedText>
          </Collapsible>
        </View>
        {/* Tree Progress - Center */}
        <View style={styles.progressSection}>
          <TreeProgress financialScore={financialScore} size={320} />
        </View>
        {/* Campaign Card - Bottom */}
        <View style={styles.campaignSection}>
          {console.log('Rendering with suggestion:', suggestion)}
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
    position: 'relative', // sync butonu için
  },
  refreshButton: {
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#DEE2E6',
    backgroundColor: '#F9F9F9',
    marginLeft: 8,
  },
  profileSection: {
    paddingBottom: 20,
  },
  campaignSection: {
    paddingHorizontal: 16,
    paddingBottom: 20,
  },
  profileRowWrap: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    marginTop: 0, // Daha yukarı
    marginBottom: 0,
  },
  badgeWrap: {
    alignSelf: 'center',
    marginTop: 4, // Daha az margin
    marginBottom: 4, // Daha az margin
    backgroundColor: '#F9F9F9',
    borderRadius: 12,
    paddingHorizontal: 18,
    paddingVertical: 6,
    borderWidth: 1,
    borderColor: '#DEE2E6',
    shadowColor: '#000',
    shadowOpacity: 0.06,
    shadowRadius: 4,
    shadowOffset: { width: 0, height: 1 },
    minWidth: 200, // Sabit minimum genişlik
    maxWidth: 250, // Maksimum genişlik sınırı
  },
  badgeText: {
    fontSize: 17,
    fontWeight: '600',
    color: '#222',
    letterSpacing: 0.2,
  },
  personalityDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    fontStyle: 'italic',
  },
  loadingOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.18)',
    alignItems: 'center',
    justifyContent: 'center',
  },

}); 