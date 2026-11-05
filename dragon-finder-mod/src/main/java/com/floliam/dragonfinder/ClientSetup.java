package com.floliam.dragonfinder;

import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraftforge.client.ClientRegistry;
import net.minecraftforge.client.gui.OverlayRegistry;
import net.minecraftforge.client.settings.KeyConflictContext;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.world.ChunkEvent;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.lwjgl.glfw.GLFW;

public final class ClientSetup {
    public static final KeyMapping TOGGLE_KEY = new KeyMapping(
            "key.dragonfinder.toggle",
            KeyConflictContext.IN_GAME,
            InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_K,
            "key.categories.dragonfinder");

    /** null = noch nicht umgeschaltet, dann gilt der Wert aus der Config. */
    private static Boolean toggledVisible;

    private ClientSetup() {
    }

    static void init() {
        FMLJavaModLoadingContext.get().getModEventBus().addListener(ClientSetup::onClientSetup);
        MinecraftForge.EVENT_BUS.addListener(ClientSetup::onClientTick);
        MinecraftForge.EVENT_BUS.addListener(ClientSetup::onChunkLoad);
    }

    private static void onClientSetup(FMLClientSetupEvent event) {
        event.enqueueWork(() -> {
            ClientRegistry.registerKeyBinding(TOGGLE_KEY);
            OverlayRegistry.registerOverlayTop("Dragon Finder", new FinderOverlay());
        });
    }

    private static void onClientTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) {
            return;
        }
        while (TOGGLE_KEY.consumeClick()) {
            toggledVisible = !isVisible();
        }
        DragonTracker.tick(Minecraft.getInstance());
    }

    private static void onChunkLoad(ChunkEvent.Load event) {
        if (event.getWorld() != null && event.getWorld().isClientSide()) {
            LairScanner.queue(event.getChunk().getPos());
        }
    }

    static boolean isVisible() {
        return toggledVisible != null ? toggledVisible : FinderConfig.SHOW_HUD.get();
    }
}
