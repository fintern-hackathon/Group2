import { useThemeColor } from '@/hooks/useThemeColor';
import { Image } from 'expo-image';
import React from 'react';
import { StyleSheet, TouchableOpacity, View } from 'react-native';
import { ThemedText } from './ThemedText';

interface CampaignCardProps {
  title: string;
  description?: string;
  imageUrl?: string;
  onPress?: () => void;
  width?: number;
  height?: number;
}

export function CampaignCard({ 
  title, 
  description, 
  imageUrl, 
  onPress,
  width = 258,
  height = 378
}: CampaignCardProps) {
  const backgroundColor = useThemeColor({}, 'background');
  const borderColor = useThemeColor({}, 'border');
  const shadowColor = useThemeColor({}, 'shadow');

  return (
    <TouchableOpacity 
      style={[
        styles.container, 
        { 
          backgroundColor, 
          borderColor,
          shadowColor,
          width,
          height
        }
      ]}
      onPress={onPress}
      activeOpacity={0.8}
    >
      <Image
        source={imageUrl ? { uri: imageUrl } : require('@/assets/images/react-logo.png')}
        style={styles.image}
        contentFit="cover"
      />
      <View style={styles.content}>
        <ThemedText style={styles.title} numberOfLines={2}>
          {title}
        </ThemedText>
        {description && (
          <ThemedText style={styles.description} numberOfLines={3}>
            {description}
          </ThemedText>
        )}
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    borderRadius: 12,
    borderWidth: 1,
    overflow: 'hidden',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  image: {
    width: '100%',
    height: '70%',
  },
  content: {
    padding: 16,
    flex: 1,
  },
  title: {
    fontSize: 16,
    fontWeight: '700',
    lineHeight: 20,
    marginBottom: 8,
  },
  description: {
    fontSize: 14,
    fontWeight: '400',
    lineHeight: 18,
    opacity: 0.8,
  },
}); 