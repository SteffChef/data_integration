"use client";

import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import Image from "next/image";
import { useRouter } from "next/navigation";

const AnimalHoverCard = ({
  name,
  imageUrl,
  children,
}: {
  name: string;
  imageUrl: string;
  children: React.ReactNode;
}) => {
  const router = useRouter();

  return (
    <Popover>
      <PopoverTrigger asChild>{children}</PopoverTrigger>
      <PopoverContent className="flex justify-center items-center flex-col gap-4">
        <h1>{name}</h1>
        <Image
          src={imageUrl}
          width={200}
          height={200}
          alt={"Fish"}
          className="rounded-md"
        />
        <Button onClick={() => router.push(`/search?animal=${name}`)}>
          Find {name}!
        </Button>
      </PopoverContent>
    </Popover>
  );
};

export default AnimalHoverCard;
