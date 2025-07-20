import { useThemeColor } from '@/hooks/useThemeColor';
import React from 'react';
import { StyleSheet, TouchableOpacity, View } from 'react-native';
import { ThemedText } from './ThemedText';

interface PopoverProps {
  message: string;
  showBackButton?: boolean;
  showNextButton?: boolean;
  onBackPress?: () => void;
  onNextPress?: () => void;
  backText?: string;
  nextText?: string;
  position?: 'top' | 'bottom';
  showRabbit?: boolean;
}

export function Popover({ 
  message,
  showBackButton = true,
  showNextButton = true,
  onBackPress,
  onNextPress,
  backText = 'Geri',
  nextText = 'Tamam',
  position = 'bottom',
  showRabbit = false
}: PopoverProps) {
  const backgroundColor = useThemeColor({}, 'white');
  const borderColor = useThemeColor({}, 'border');
  const shadowColor = useThemeColor({}, 'shadow');
  const textColor = useThemeColor({}, 'textSecondary');
  const primaryColor = useThemeColor({}, 'primary');
  const grayColor = useThemeColor({}, 'lightGray');

  return (
    <View style={[
      styles.container, 
      { 
        backgroundColor, 
        borderColor,
        shadowColor,
        marginTop: position === 'bottom' ? 8 : 0,
        marginBottom: position === 'top' ? 8 : 0,
      }
    ]}>
      {/* Arrow */}
      <View style={[
        styles.arrow,
        { 
          borderBottomColor: position === 'bottom' ? backgroundColor : 'transparent',
          borderTopColor: position === 'top' ? backgroundColor : 'transparent',
          top: position === 'bottom' ? -8 : undefined,
          bottom: position === 'top' ? -8 : undefined,
        }
      ]} />
      
      {/* Content */}
      <View style={styles.content}>
        <ThemedText style={[styles.message, { color: textColor }]}>
          {message}
        </ThemedText>
        {showRabbit && (
          <View style={styles.rabbitContainer}>
            <View style={styles.rabbit}>
              <View style={styles.rabbitBody} />
              <View style={styles.rabbitEars}>
                <View style={styles.rabbitEar} />
                <View style={styles.rabbitEar} />
              </View>
              <View style={styles.rabbitNose} />
            </View>
          </View>
        )}
      </View>
      
      {/* Actions */}
      {(showBackButton || showNextButton) && (
        <View style={[styles.actions, { borderTopColor: borderColor }]}>
          {showBackButton && (
            <TouchableOpacity onPress={onBackPress} style={styles.actionButton}>
              <ThemedText style={[styles.actionText, { color: grayColor }]}>
                {backText}
              </ThemedText>
            </TouchableOpacity>
          )}
          
          {showNextButton && (
            <TouchableOpacity onPress={onNextPress} style={styles.actionButton}>
              <ThemedText style={[styles.actionText, { color: primaryColor }]}>
                {nextText}
              </ThemedText>
            </TouchableOpacity>
          )}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    borderRadius: 12,
    borderWidth: 1,
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.12,
    shadowRadius: 40,
    elevation: 8,
    position: 'relative',
  },
  arrow: {
    position: 'absolute',
    left: 20,
    width: 0,
    height: 0,
    borderLeftWidth: 10,
    borderRightWidth: 10,
    borderTopWidth: 8,
    borderBottomWidth: 8,
    borderLeftColor: 'transparent',
    borderRightColor: 'transparent',
  },
  content: {
    padding: 12,
  },
  message: {
    fontSize: 13,
    fontWeight: '700',
    lineHeight: 16,
  },
  actions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 12,
    borderTopWidth: 1,
  },
  actionButton: {
    paddingVertical: 4,
  },
  actionText: {
    fontSize: 14,
    fontWeight: '700',
    lineHeight: 18,
  },
  rabbitContainer: {
    position: 'absolute',
    bottom: -10,
    right: -10,
  },
  rabbit: {
    position: 'relative',
    width: 30,
    height: 30,
  },
  rabbitBody: {
    width: 20,
    height: 20,
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    position: 'absolute',
    bottom: 0,
    right: 0,
  },
  rabbitEars: {
    position: 'absolute',
    top: -5,
    right: 5,
    flexDirection: 'row',
    gap: 2,
  },
  rabbitEar: {
    width: 6,
    height: 12,
    backgroundColor: '#FFB6C1',
    borderRadius: 3,
  },
  rabbitNose: {
    width: 4,
    height: 4,
    backgroundColor: '#FF69B4',
    borderRadius: 2,
    position: 'absolute',
    bottom: 8,
    right: 8,
  },
}); 