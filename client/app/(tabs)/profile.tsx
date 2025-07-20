import { ThemedText } from '@/components/ThemedText';
import { TopBar } from '@/components/TopBar';
import React, { useState } from 'react';
import { Image, ScrollView, StyleSheet, Switch, TouchableOpacity, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function ProfileScreen() {
  const [notificationsEnabled, setNotificationsEnabled] = useState(false);

  return (
    <SafeAreaView style={styles.container} edges={[]}>  
      <TopBar title="Profil" />
      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* Profil Fotoğrafı ve İsim */}
        <View style={styles.profileHeader}>
          <Image source={require('@/assets/images/pp.png')} style={styles.avatar} />
          <ThemedText style={styles.profileName}>Alican Yılmaz</ThemedText>
        </View>

        {/* Ayarlar Kartları */}
        <View style={styles.cardList}>
          <TouchableOpacity style={styles.card}>
            <ThemedText style={styles.cardText}>Kişisel Bilgiler</ThemedText>
            <ThemedText style={styles.cardArrow}>›</ThemedText>
          </TouchableOpacity>
          <TouchableOpacity style={styles.card}>
            <ThemedText style={styles.cardText}>Bildirimler</ThemedText>
            <ThemedText style={styles.cardArrow}>›</ThemedText>
          </TouchableOpacity>
          <TouchableOpacity style={styles.card}>
            <ThemedText style={styles.cardText}>Ayarlar</ThemedText>
            <ThemedText style={styles.cardArrow}>›</ThemedText>
          </TouchableOpacity>
        </View>

        {/* Bağlı Bankalar */}
        <View style={styles.sectionHeaderWrap}>
          <ThemedText style={styles.sectionHeader}>Bağlı Bankalar / Kurumlar</ThemedText>
        </View>
        <View style={styles.bankList}>
          <TouchableOpacity style={styles.bankCard}>
            <Image source={require('@/assets/images/halkbank.png')} style={styles.bankIcon} />
            <ThemedText style={styles.bankName}>Halkbank</ThemedText>
            <ThemedText style={styles.cardArrow}>›</ThemedText>
          </TouchableOpacity>
          <TouchableOpacity style={styles.bankCard}>
            <Image source={require('@/assets/images/isbank.png')} style={styles.bankIcon} />
            <ThemedText style={styles.bankName}>İş Bankası</ThemedText>
            <ThemedText style={styles.cardArrow}>›</ThemedText>
          </TouchableOpacity>
          <TouchableOpacity style={styles.bankCard}>
            <Image source={require('@/assets/images/ziraat.png')} style={styles.bankIcon} />
            <ThemedText style={styles.bankName}>Ziraat Bankası</ThemedText>
            <ThemedText style={styles.cardArrow}>›</ThemedText>
          </TouchableOpacity>
        </View>

        {/* Bildirim Switch'i */}
        <View style={styles.switchRow}>
          <ThemedText style={styles.switchLabel}>Bildirimler</ThemedText>
          <Switch
            value={notificationsEnabled}
            onValueChange={setNotificationsEnabled}
            trackColor={{ false: '#B0B0B0', true: '#0057B8' }}
            thumbColor={notificationsEnabled ? '#fff' : '#fff'}
          />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9F9F9',
  },
  scrollContent: {
    paddingBottom: 32,
  },
  profileHeader: {
    alignItems: 'center',
    marginTop: 24,
    marginBottom: 16,
  },
  avatar: {
    width: 72,
    height: 72,
    borderRadius: 36,
    borderWidth: 3,
    borderColor: '#0057B8',
    marginBottom: 8,
  },
  profileName: {
    fontSize: 18,
    fontWeight: '700',
    color: '#222',
  },
  cardList: {
    marginHorizontal: 16,
    marginBottom: 18,
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 10,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 14,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#F0F0F0',
  },
  cardText: {
    flex: 1,
    fontSize: 15,
    color: '#222',
    fontWeight: '500',
  },
  cardArrow: {
    fontSize: 22,
    color: '#B0B0B0',
    fontWeight: '400',
    marginLeft: 8,
  },
  sectionHeaderWrap: {
    marginHorizontal: 16,
    marginTop: 8,
    marginBottom: 2,
  },
  sectionHeader: {
    fontSize: 13,
    color: '#888',
    fontWeight: '600',
  },
  bankList: {
    marginHorizontal: 16,
    marginBottom: 18,
  },
  bankCard: {
    backgroundColor: '#fff',
    borderRadius: 10,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 14,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#F0F0F0',
  },
  bankIcon: {
    width: 32,
    height: 32,
    borderRadius: 8,
    marginRight: 12,
  },
  bankName: {
    flex: 1,
    fontSize: 15,
    color: '#222',
    fontWeight: '500',
  },
  switchRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginHorizontal: 16,
    marginTop: 12,
    backgroundColor: '#fff',
    borderRadius: 10,
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderWidth: 1,
    borderColor: '#F0F0F0',
  },
  switchLabel: {
    fontSize: 15,
    color: '#222',
    fontWeight: '500',
  },
}); 