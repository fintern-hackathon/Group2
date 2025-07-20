import React from 'react';
import { Image, StyleSheet, TouchableOpacity, View } from 'react-native';
import { ThemedText } from './ThemedText';

interface CampaignCardProps {
  onConfirm?: () => void;
  onCancel?: () => void;
}

export function CampaignCard({ onConfirm, onCancel }: CampaignCardProps) {
  return (
    <View style={styles.card}>
      <View style={styles.contentRow}>
        <View style={styles.textContainer}>
          <ThemedText style={styles.text}>
            Lorem ipsum dolor sit amet consectetur. Sedet pellentesque nisi at sed massa massa tellus ut mattis. Elementum viverra sagittis elementum.
          </ThemedText>
        </View>
        <Image
          source={require('@/assets/images/bunny.png')}
          style={styles.bunny}
          resizeMode="contain"
        />
      </View>
      <View style={styles.buttonRow}>
        <TouchableOpacity onPress={onCancel}>
          <ThemedText style={styles.cancel}>Geri</ThemedText>
        </TouchableOpacity>
        <TouchableOpacity onPress={onConfirm}>
          <ThemedText style={styles.confirm}>Tamam</ThemedText>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    marginHorizontal: 16,
    marginTop: 16,
    backgroundColor: '#fff',
    borderRadius: 16,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 2 },
    elevation: 4,
  },
  contentRow: {
    position: 'relative',
    padding: 12,
    marginBottom: 8,
  },
  textContainer: {
    flex: 1,
    paddingRight: 60,
  },
  text: {
    fontSize: 12,
    color: '#333',
    lineHeight: 16,
  },
  bunny: {
    position: 'absolute',
    bottom: 0,
    right: 0,
    width: 65,
    height: 65,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 12,
    paddingBottom: 12,
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
