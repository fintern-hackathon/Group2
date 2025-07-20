import React, { useEffect, useState } from 'react';
import { Alert, ScrollView, StyleSheet, TouchableOpacity, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { BottomNavigation } from '@/components/BottomNavigation';
import { CampaignCard } from '@/components/CampaignCard';
import { ProfileHeader } from '@/components/ProfileHeader';
import { ThemedText } from '@/components/ThemedText';
import { TopBar } from '@/components/TopBar';
import { TreeProgress } from '@/components/TreeProgress';
import { IconSymbol } from '@/components/ui/IconSymbol';
import { useThemeColor } from '@/hooks/useThemeColor';

export default function IndexScreen() {
  const [activeTab, setActiveTab] = useState('campaigns');
  const [financialScore, setFinancialScore] = useState(75); // Varsayılan skor
  const [suggestion, setSuggestion] = useState('');
  const [selectedMonth, setSelectedMonth] = useState('Ocak');
  const [showMonthDropdown, setShowMonthDropdown] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const months = [
    'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
    'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'
  ];

  // Skoru backend'den çek
  useEffect(() => {
    const fetchScore = async () => {
      try {
        const response = await fetch('http://localhost:8006/api/v1/analytics/1/score');
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
        const response = await fetch('http://localhost:8006/api/v1/mcp-client/daily-suggestion', {
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

  const handleRefresh = () => {
    setIsRefreshing(true);
    // Burada veri yenileme işlemi yapılabilir
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor }]} edges={[]}>
      <TopBar title="FinTree" />

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
        {/* Profile Header + Ay Dropdown + Refresh + Badge */}
        <View style={styles.profileRowWrap}>
          <View style={{ flex: 1 }}>
            <ProfileHeader userName="Alican" greeting="İyi günler," />
          </View>
          <View style={styles.monthDropdownWrap}>
            <View>
              <TouchableOpacity style={styles.monthDropdown} onPress={() => setShowMonthDropdown(!showMonthDropdown)}>
                <IconSymbol name="calendar" size={18} color="#0057B8" style={{ marginRight: 4 }} />
                <ThemedText style={styles.monthDropdownText}>
                  {selectedMonth}
                </ThemedText>
                <IconSymbol name="chevron.right" size={18} color="#0057B8" style={{ transform: [{ rotate: showMonthDropdown ? '90deg' : '0deg' }] }} />
              </TouchableOpacity>
              {showMonthDropdown && (
                <View style={styles.dropdownList}>
                  {months.map((m) => (
                    <ThemedText key={m} style={styles.dropdownItem} onPress={() => { setSelectedMonth(m); setShowMonthDropdown(false); }}>{m}</ThemedText>
                  ))}
                </View>
              )}
            </View>
            <TouchableOpacity style={styles.refreshBtn} onPress={handleRefresh}>
              <IconSymbol name="sync" size={22} color={'#0000'} />
            </TouchableOpacity>
          </View>
        </View>
        <View style={styles.badgeWrap}>
          <ThemedText style={styles.badgeText}>Savurgan</ThemedText>
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
  profileRowWrap: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    marginTop: 8,
    marginBottom: 0,
  },
  monthDropdownWrap: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  monthDropdown: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#B0B0B0',
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 4,
    marginRight: 4,
    backgroundColor: '#fff',
    position: 'relative', // dropdown'un absolute pozisyonu için
  },
  monthDropdownText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#333',
    marginRight: 4,
  },
  dropdownList: {
    position: 'absolute',
    top: 32,
    left: 0,
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#B0B0B0',
    borderRadius: 8,
    zIndex: 10,
    width: 100,
    elevation: 8,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 2 },
  },
  dropdownItem: {
    padding: 8,
    fontSize: 15,
    color: '#333',
  },
  refreshBtn: {
    marginLeft: 4,
    padding: 6,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#B0B0B0',
    backgroundColor: '#Fff',
  },
  badgeWrap: {
    alignSelf: 'center',
    marginTop: 8,
    marginBottom: 8,
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
  },
  badgeText: {
    fontSize: 17,
    fontWeight: '600',
    color: '#222',
    letterSpacing: 0.2,
  },
}); 