using UnrealBuildTool;

public class UE_ADE_DemoEditorTarget : TargetRules
{
	public UE_ADE_DemoEditorTarget(TargetInfo Target) : base(Target)
	{
		DefaultBuildSettings = BuildSettingsVersion.Latest;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		Type = TargetType.Editor;
		ExtraModuleNames.Add("UE_ADE_Demo");
	}
}
