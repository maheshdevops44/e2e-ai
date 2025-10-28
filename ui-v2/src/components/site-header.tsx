"use client"

import { usePathname } from "next/navigation"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
// COMMENTED OUT FOR NOW - WILL NEED LATER
// import { useSession, signOut } from "next-auth/react"

interface SiteHeaderProps {
  title?: string;
  subtitle?: string;
}

export function SiteHeader({ title, subtitle }: SiteHeaderProps) {
  const pathname = usePathname()
  
  // Determine title based on current route if not explicitly provided
  const getPageTitle = () => {
    if (title) return title
    
    if (pathname === '/dashboard') {
      return "Dashboard"
    } else if (pathname === '/create-test' || pathname.startsWith('/create-test/workflow')) {
      return "Create New Test"
    } else if (pathname === '/archive') {
      return "Archive"
    } else if (pathname === '/files') {
      return "Files"
    } else {
      return "Dashboard"
    }
  }

  return (
    <header className="flex h-16 shrink-0 items-center gap-4 px-4 transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12">
      {/* Breadcrumb Navigation */}
      <div className="flex items-center gap-2">
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem className="hidden md:block">
              <BreadcrumbLink href="#">
                {getPageTitle()}
              </BreadcrumbLink>
            </BreadcrumbItem>
            {subtitle && (
              <>
                <BreadcrumbSeparator className="hidden md:block" />
                <BreadcrumbItem>
                  <BreadcrumbPage>{subtitle}</BreadcrumbPage>
                </BreadcrumbItem>
              </>
            )}
          </BreadcrumbList>
        </Breadcrumb>
      </div>
    </header>
  )
}