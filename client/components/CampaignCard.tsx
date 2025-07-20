import React from 'react';
import { Image, StyleSheet, View } from 'react-native';
import { ThemedText } from './ThemedText';

interface CampaignCardProps {
  onConfirm?: () => void;
  onCancel?: () => void;
  description?: string;
}

export function CampaignCard({ onConfirm, onCancel, description }: CampaignCardProps) {
  return (
    <View style={styles.cardShadowWrap}>
      <View style={styles.card}>
        <View style={styles.contentRow}>
          <View style={styles.textContainer}>
            <ThemedText style={styles.text}>
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
    minHeight:124,
    position: 'relative',
  },
  contentRow: {
    minHeight: 0,
    position: 'relative',
    marginBottom: 0,
  },
  textContainer: {
    padding:12,
    flex: 1,
    display:'flex',
    height:'100%',
    width:'100%'
  },
  text: {
    fontSize: 14,
    color: '#333',
    fontWeight:'500'
  },
  bunny: {
    alignSelf: 'flex-end',
    width: 100,
    height: 100,
    marginTop: 'auto',
    borderBottomRightRadius: 16,
    marginBottom: -4, 
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
