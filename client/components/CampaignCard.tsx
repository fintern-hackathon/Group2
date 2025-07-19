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
        <View style={{ flex: 1 }}>
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
    marginTop: 24,
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 16,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 2 },
    elevation: 4,
  },
  contentRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  text: {
    fontSize: 13,
    color: '#333',
    marginRight: 12,
  },
  bunny: {
    width: 50,
    height: 50,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
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
