import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "./ui/sidebar";
import { TiHome } from "react-icons/ti";
import { FaMapMarkedAlt } from "react-icons/fa";
import { FaSearch } from "react-icons/fa";
import { IoFish } from "react-icons/io5";
import UserProfile from "./UserProfile";
import { createClient } from "@/supabase/server";
import Link from "next/link";

const AppSidebar = async () => {
  const supabase = await createClient();

  const {
    data: { user },
  } = await supabase.auth.getUser();

  const headerLinks = [
    {
      name: "Home",
      href: "/",
      icon: TiHome,
      iconSize: 20,
    },
    {
      name: "Search",
      href: "/search",
      icon: FaSearch,
      iconSize: 18,
    },
    {
      name: "Map",
      href: "/map",
      icon: FaMapMarkedAlt,
      iconSize: 20,
    },
    {
      name: "Animals",
      href: "/animals",
      icon: IoFish,
      iconSize: 20,
    },
  ];

  return (
    <Sidebar side="left">
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {headerLinks.map((link) => (
                <SidebarMenuItem key={link.name}>
                  <SidebarMenuButton asChild>
                    <a href={link.href}>
                      <link.icon />
                      <span>{link.name}</span>
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        {user ? (
          <UserProfile />
        ) : (
          <>
            <Link href="/login" className="text-white hover:opacity-75">
              Login
            </Link>
            <Link href="/sign-up" className="text-white hover:opacity-75">
              Sign Up
            </Link>
          </>
        )}
      </SidebarFooter>
    </Sidebar>
  );
};

export default AppSidebar;
