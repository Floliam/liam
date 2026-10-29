package com.floliam.locatorbar;

import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.KeyMapping;
import net.minecraftforge.client.ClientRegistry;
import net.minecraftforge.client.gui.ForgeIngameGui;
import net.minecraftforge.client.gui.OverlayRegistry;
import net.minecraftforge.client.settings.KeyConflictContext;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.lwjgl.glfw.GLFW;

public final class ClientSetup {
    public static final KeyMapping TOGGLE_KEY = new KeyMapping(
            "key.playerlocatorbar.toggle",
            KeyConflictContext.IN_GAME,
            InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_J,
            "key.categories.playerlocatorbar");

    /** null = noch nicht umgeschaltet, dann gilt der Wert aus der Config. */
    private static Boolean toggledVisible;

    private ClientSetup() {
    }

    static void init() {
        FMLJavaModLoadingContext.get().getModEventBus().addListener(ClientSetup::onClientSetup);
        MinecraftForge.EVENT_BUS.addListener(ClientSetup::onClientTick);
    }

    private static void onClientSetup(FMLClientSetupEvent event) {
        event.enqueueWork(() -> {
            ClientRegistry.registerKeyBinding(TOGGLE_KEY);
            // Direkt nach der Hotbar zeichnen, also vor Herzen/Hunger, damit diese nach oben ausweichen können.
            OverlayRegistry.registerOverlayAbove(ForgeIngameGui.HOTBAR_ELEMENT, "Player Locator Bar", new LocatorBarOverlay());
        });
    }

    private static void onClientTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) {
            return;
        }
        while (TOGGLE_KEY.consumeClick()) {
            toggledVisible = !isVisible();
        }
    }

    static boolean isVisible() {
        return toggledVisible != null ? toggledVisible : LocatorConfig.ENABLED.get();
    }
}
