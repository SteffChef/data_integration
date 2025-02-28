"use client";

import React, { useEffect, useState } from "react";
import { Button } from "./ui/button";
import { LogOut } from "lucide-react";
// import {Settings, User as UserIcon} from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar";
import { useRouter } from "next/navigation";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import { User } from "@supabase/supabase-js";
import { createClient } from "@/supabase/client";

const UserProfile = () => {
  const router = useRouter();

  const supabase = createClient();

  const [user, setUser] = useState<User | null>(null);

  const getUser = async () => {
    const { data, error } = await supabase.auth.getUser();
    if (error) {
      console.log(error.message);
    }
    setUser(data.user);
  };

  useEffect(() => {
    getUser();
  }, []);

  const signOut = async () => {
    await supabase.auth.signOut();
    return router.refresh();
  };
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="icon" className="rounded-full">
          <Avatar className="hover:opacity-75 transition cursor-pointer">
            <AvatarImage src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQatiCBz67xlO9FWdp4fEvHBOCdlPxoNEjPvA&s" />
            <AvatarFallback>TU</AvatarFallback>
          </Avatar>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <div className="px-2 py-1">
          <p className="font-semibold">Test User</p>
          <p className="text-xs text-secondary-foreground">{user?.email}</p>
        </div>
        <DropdownMenuSeparator />
        {/* <DropdownMenuItem onClick={() => {}} disabled>
          <UserIcon className="mr-2 h-4 w-4" />
          Profile
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => {}} disabled>
          <Settings className="mr-2 h-4 w-4" />
          Settings
        </DropdownMenuItem>
        <DropdownMenuSeparator /> */}
        <DropdownMenuItem onClick={signOut}>
          <LogOut className="mr-2 h-4 w-4" />
          Logout
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default UserProfile;
