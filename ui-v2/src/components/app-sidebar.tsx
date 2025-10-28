"use client"

import * as React from "react"
import { useRouter, usePathname } from 'next/navigation'
import {
  Settings,
  User,
  LayoutDashboard,
  SquarePlus,
  Archive,
  Files,
  Bell,
} from "@/components/icons"

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
} from "@/components/ui/sidebar"

interface AppSidebarProps extends React.ComponentProps<typeof Sidebar> {
  className?: string
}

export function AppSidebar({ ...props }: AppSidebarProps) {
  const router = useRouter();
  const pathname = usePathname();

  const handleNavigation = (path: string) => {
    router.push(path);
  };

  const getButtonStyles = (path: string, variant: 'current' | 'focused' | 'default' = 'default') => {
    let isActive = false;
    if (path === '/dashboard') {
      isActive = pathname === '/dashboard';
    } else if (path === '/create-test') {
      // Active for create-test page and workflow pages (since workflows are part of test creation)
      isActive = pathname === '/create-test' || pathname.startsWith('/create-test/workflow');
    } else {
      isActive = pathname === path;
    }

    const baseStyle = {
      width: '32px',
      height: '32px',
      paddingTop: 'var(--spacing-2, 0.5rem)',
      paddingRight: 'var(--spacing-1, 0.25rem)', 
      paddingBottom: 'var(--spacing-2, 0.5rem)',
      paddingLeft: 'var(--spacing-1, 0.25rem)',
      gap: '8px',
      opacity: 1,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      cursor: 'pointer',
      transition: 'all 0.2s ease'
    };

    if (isActive && variant === 'current') {
      return {
        ...baseStyle,
        borderRadius: 'var(--border-radius-rounded-full, 9999px)',
        background: 'var(--base-primary, #171717)',
        color: '#FFFFFF'
      };
    } else if (variant === 'focused') {
      return {
        ...baseStyle,
        borderRadius: 'var(--border-radius-rounded-lg, 0.5rem)',
        background: 'var(--base-accent, #F5F5F5)',
        color: '#000000'
      };
    } else {
      return {
        ...baseStyle,
        borderRadius: 'var(--border-radius-rounded-lg, 0.5rem)',
        background: 'transparent',
        color: '#6B7280'
      };
    }
  };

  return (
    <Sidebar collapsible="icon" className="!w-14 z-50" {...props}>
      <SidebarContent className="p-1.5">
        <div className="flex flex-col gap-1.5">
          {/* Dashboard - Default State */}
          <button 
            onClick={() => handleNavigation('/dashboard')} 
            style={getButtonStyles('/dashboard', 'default')}
          >
            <LayoutDashboard style={{ width: '20px', height: '20px' }} />
          </button>
          
          {/* Create Test Case - Current State */}
          <button 
            onClick={() => handleNavigation('/create-test')} 
            style={getButtonStyles('/create-test', 'current')}
          >
            <SquarePlus style={{ width: '20px', height: '20px' }} />
          </button>
          
          {/* Archive - Focused State */}
          <button 
            onClick={() => handleNavigation('/archive')} 
            style={getButtonStyles('/archive', 'focused')}
          >
            <Archive style={{ width: '20px', height: '20px' }} />
          </button>
          
          {/* Files - Default State */}
          <button 
            onClick={() => handleNavigation('/files')} 
            style={getButtonStyles('/files', 'default')}
          >
            <Files style={{ width: '20px', height: '20px' }} />
          </button>
          
          {/* Notifications - Default State */}
          <button 
            onClick={() => handleNavigation('/notifications')} 
            style={getButtonStyles('/notifications', 'default')}
          >
            <Bell style={{ width: '20px', height: '20px' }} />
          </button>
          
          {/* Settings */}
          <button 
            onClick={() => handleNavigation('/settings')} 
            style={getButtonStyles('/settings', 'default')}
          >
            <Settings style={{ width: '20px', height: '20px' }} />
          </button>
        </div>
      </SidebarContent>
      <SidebarFooter className="p-1.5 mt-auto">
        <div className="w-8 h-8 bg-black rounded-full flex items-center justify-center">
          <User className="w-5 h-5 text-white" />
        </div>
      </SidebarFooter>
    </Sidebar>
  )
}
