import React from 'react';
import { Image, StyleSheet, View } from 'react-native';
import { ThemedText } from './ThemedText';

interface CampaignCardProps {
  onConfirm?: () => void;
  onCancel?: () => void;
  description?: string;
}

export function CampaignCard({ onConfirm, onCancel, description }: CampaignCardProps) {
  console.log('CampaignCard received description:', description);
  console.log('CampaignCard description type:', typeof description);
  return (
    <View style={styles.cardShadowWrap}>
      <View style={styles.card}>
        <View style={styles.contentRow}>
          <View style={styles.textContainer}>
            <ThemedText style={styles.text} numberOfLines={6}>
              {description || 'Lorem ipsum dolor sit amet consectetur. Sedet pellentesque nisi at sed massa massa tellus ut mattis. Elementum viverra sagittis elementum.'}
            </ThemedText>
          </View>
          <Image
            source={require('@/assets/images/bunny.png')}
            style={styles.bunny}
            resizeMode="contain"
          />
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  cardShadowWrap: {
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 2 },
    elevation: 4,
    borderRadius: 16,
    marginHorizontal: 16,
    marginTop: 16,
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 16,
    overflow: 'hidden',
    height: 160, // Daha da büyük yükseklik
    position: 'relative',
  },
  contentRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    height: '100%',
  },
  textContainer: {
    padding: 12,
    flex: 1,
    justifyContent: 'flex-start', // Yukarıdan başla
    paddingTop: 15, // Biraz aşağıdan başla ki sığsın
    paddingRight: 80, // Tavşan için daha az yer bırak
  },
  text: {
    fontSize: 12,
    color: '#333',
    fontWeight: '500',
    lineHeight: 18, // Satır yüksekliği
  },
  bunny: {
    position: 'absolute',
    right: 0,
    bottom: 0,
    width: 100,
    height: 100,
    borderBottomRightRadius: 16,
    zIndex: -1, // Yazının arkasında kalacak
  },
  cancel: {
    fontSize: 14,
    color: '#666',
  },
  confirm: {
    fontSize: 14,
    fontWeight: '700',
    color: '#0057B8',
  },
});
