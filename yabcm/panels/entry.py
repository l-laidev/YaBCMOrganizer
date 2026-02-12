import wx
from pubsub import pub
from wx.lib.scrolledpanel import ScrolledPanel
from pyxenoverse.bcm import address_to_index, index_to_address
from pyxenoverse.gui import add_entry, EVT_RESULT, EditThread
from pyxenoverse.gui.ctrl.dummy_ctrl import DummyCtrl
from pyxenoverse.gui.ctrl.hex_ctrl import HexCtrl
from pyxenoverse.gui.ctrl.multiple_selection_box import MultipleSelectionBox
from pyxenoverse.gui.ctrl.single_selection_box import SingleSelectionBox

from yabcm.my_helpers import convert_to_px


MAX_UINT16 = 0xFFFF
MAX_UINT32 = 0xFFFFFFFF
LABEL_STYLE = wx.ALIGN_CENTER_VERTICAL | wx.ALL


class Page(ScrolledPanel):
    def __init__(self, parent, rows=32):
        ScrolledPanel.__init__(self, parent)
        self.sizer = wx.FlexGridSizer(rows=rows, cols=2, hgap=convert_to_px(5), vgap=convert_to_px(5, False))
        self.SetSizer(self.sizer)
        self.SetupScrolling()


class EntryPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent_panel = parent
        self.entry = None
        self.notebook = wx.Notebook(self)
        self.edit_thread = None
        button_input_panel = Page(self.notebook)
        activator_panel = Page(self.notebook)
        bac_panel = Page(self.notebook)
        misc_panel = Page(self.notebook)
        unknown_panel = Page(self.notebook)

        self.notebook.AddPage(button_input_panel, 'Inputs')
        self.notebook.AddPage(activator_panel, 'Activator')
        self.notebook.AddPage(bac_panel, 'BAC')
        self.notebook.AddPage(misc_panel, 'Misc')
        self.notebook.AddPage(unknown_panel, 'Unknown')

        sizer = wx.BoxSizer()
        sizer.Add(self.notebook, 1, wx.ALL | wx.EXPAND, 10)

        self.address = DummyCtrl()
        self.sibling = self.add_num_entry(misc_panel, 'Sibling Idx', min=0, max=0x7FFFFFFF)
        self.parent = DummyCtrl()
        self.child = self.add_num_entry(misc_panel, 'Child Idx', min=0, max=0x7FFFFFFF)
        self.root = DummyCtrl()

        # u_00
        self.u_00 = self.add_hex_entry(unknown_panel, 'U_00', max=MAX_UINT32)

        # directional input
        self.directional_input = self.add_multiple_selection_entry(
            button_input_panel, 'Directional Input', cols=2, orient=wx.VERTICAL, choices=[
                ('User Direction', ['Input activated once', 'Up', 'Down', 'Right', 'Left'], True),
                ('Relative Direction', ['Forwards', 'Backwards', 'Left', 'Right'], True)
            ])

        # Button input
        self.button_input = self.add_multiple_selection_entry(
            button_input_panel, 'Button Input', title='0xABCDEFGH', cols=3, orient=wx.VERTICAL, choices=[
                ('B/C', ['Lock On', 'Descend', 'Dragon Radar', 'Jump', 'Ultimate attack'], True),
                ('D', ['Skill input', 'Skill display + skill input', 'Ultimate attack + skill input', None], True),
                ('E', None, True),
                ('F', ['Skill display + weak attack', 'Skill display + strong attack',
                       'Skill display + ki blast', 'Skill display + jump'], True),
                ('G', ['Skill display', 'Boost/step', 'Block', None], True),
                ('H', ['Weak attack', 'Strong attack', 'Ki blast', 'Jump'], True)
            ])

        # Hold Down Conditions
        self.hold_down_conditions = self.add_multiple_selection_entry(
            button_input_panel, 'Hold Down\nConditions', majorDimension=1, choices=[
                ('Charge Type', {
                    'Automatic': 0x0,
                    'Manual': 0x1,
                    'Unknown (0x2)': 0x2,
                    'Unknown (0x3)': 0x3,
                    'Unknown (0x4)': 0x4,
                }, False),
                ('Options #2', {
                    'Unknown (0x0)': 0x0,
                    'Unknown (0x1)': 0x1,
                    'Unknown (0x2)': 0x2,
                    'Unknown (0x3)': 0x3,
                    'Unknown (0x4)': 0x4,
                }, False),
                ('Options #3', {
                    'Unknown (0x0)': 0x0,
                    'Unknown (0x1)': 0x1,
                    'Unknown (0x2)': 0x2,
                    'Unknown (0x3)': 0x3,
                    'Unknown (0x4)': 0x4,
                }, False),
                ('Options #4', {
                    'Unknown (0x0)': 0x0,
                    'Unknown (0x1)': 0x1,
                    'Unknown (0x2)': 0x2,
                    'Unknown (0x3)': 0x3,
                    'Unknown (0x4)': 0x4,
                }, False),
                ('Action', {
                    'Continue until released': 0x0,
                    'Delay until released': 0x1,
                    'Unknown (0x2)': 0x2,
                    'Unknown (0x3)': 0x3,
                    'Stop skill from activating': 0x4,
                }, False)
        ])

        self.opponent_size_conditions = self.add_multiple_selection_entry(
            activator_panel, 'Misc\nConditions', cols=4, orient=wx.VERTICAL, choices=[
                ('Skill Upgrade 1', ["Unk (0x1)", "Unk (0x2)",
                            "Unk (0x4)", "Unk (0x8)"], True),
                ('Skill Upgrade 2', ["Unk (0x1)", "Unk (0x2)",
                            "Unk (0x4)", "Unk (0x8)"], True),
                ('Opponent Size 1', ["Unk (0x1)", "Unk (0x2)",
                            "Unk (0x4)", "Unk (0x8)"], True),
                ('Opponent Size 2', ["Unk (0x1)", "Unk (0x2)",
                            "Unk (0x4)", "Unk (0x8)"], True),
                ('Unk Size 1', ["Unk (0x1)", "Unk (0x2)",
                            "Unk (0x4)", "Unk (0x8)"], True),
                ('Unk Size 2', ["Unk (0x1)", "Unk (0x2)",
                            "Unk (0x4)", "Unk (0x8)"], True),
                ('Unk Size 3', ["Unk (0x1)", "Unk (0x2)",
                            "Unk (0x4)", "Unk (0x8)"], True),
                ('Unk Size 4', ["Unk (0x1)", "Unk (0x2)",
                            "Unk (0x4)", "Unk (0x8)"], True),
            ])

        # Minimum Loop Duration
        self.minimum_loop_duration = self.add_num_entry(
            activator_panel, 'Minimum Loop\nConditions', True)

        # Maximum Loop Duration
        self.maximum_loop_duration = self.add_num_entry(
            activator_panel, 'Maximum Loop\nConditions', True)

        # Primary Activator Conditions
        self.primary_activator_conditions = self.add_multiple_selection_entry(
            activator_panel, 'Primary Activator\nConditions', cols=3, orient=wx.VERTICAL, choices=[
                ('Health', ["User's Health (One Use)", "Target's health < 25%",
                            "When Running BAC Entry Attack Hits", "User's Health"], True),
                ('Collision/stamina', ["Active Projectile", 'Stamina > 0%', 'Not near map ceiling', 'Not near certain objects'], True),
                ('Targeting', ["Opponent Knockback", None, 'Targeting Opponent'], True),
                ('Touching', [None, None, 'Ground', 'Opponent'], True),
                ('Counter and ki amount', ['Counter melee', 'Counter projectile', 'Ki < 100%', 'Ki > 0%'], True),
                ('Primary activator', ['Transformed', 'Flash on/off unless targeting', None, 'Not Moving'], True),
                ('Distance and transformation', ['Attack Pass on Opponent Guard', 'Close', 'Far', 'Base form'], True),
                ('Position', ['Standing', 'Floating', 'Touching "ground"', 'When an attack hits'], True)
            ])

        # Activator State
        self.activator_state = self.add_multiple_selection_entry(
            activator_panel, 'Activator State', cols=2, orient=wx.VERTICAL, choices=[
                ('', ['Forwards', 'Backwards', 'Left', 'Right'], True),
                ('', ['Receiving Damage', 'Jumping', 'Not being damaged', 'Target attacking player'], True),
                ('', ['Idle', 'Combo/skill', 'Boosting', 'Guarding'], True)
            ])

        # BAC Stuff
        self.bac_entry_primary = self.add_num_entry(bac_panel, 'BAC Entry Primary', True)
        self.bac_entry_charge = self.add_num_entry(bac_panel, 'BAC Entry Charge', True)
        self.u_24 = self.add_hex_entry(unknown_panel, 'U_24', max=MAX_UINT16)
        self.bac_entry_user_connect = self.add_num_entry(bac_panel, 'BAC Entry\nUser Connect', True)
        self.bac_entry_victim_connect = self.add_num_entry(bac_panel, 'BAC Entry\nVictim Connect', True)
        self.bac_entry_airborne = self.add_num_entry(bac_panel, 'BAC Entry Airborne', True)
        self.bac_entry_unknown = self.add_num_entry(bac_panel, 'BAC Entry Targetting Override', True)
        self.random_flag = self.add_multiple_selection_entry(bac_panel, 'Unknown BAC Flags', majorDimension=2, choices=[
            ('', {
                'None': 0x0,
                'Random BAC Entry': 0x1,
                'No Target Correction': 0x2,
                '3 Instance Setup': 0x3,
                'Unknown (0x4)': 0x4,
                'Unknown (0x5)': 0x6,
            }, False)
        ])

        self.ki_cost = self.add_num_entry(misc_panel, 'Ki Cost', True)
        self.u_44 = self.add_hex_entry(unknown_panel, 'U_44', max=MAX_UINT32)
        self.u_48 = self.add_hex_entry(unknown_panel, 'U_48', max=MAX_UINT32)
        self.receiver_link_id = self.add_hex_entry(misc_panel, 'Receiver Link Id', max=MAX_UINT32)
        self.u_50 = self.add_hex_entry(unknown_panel, 'U_50', max=MAX_UINT32)
        self.stamina_cost = self.add_num_entry(misc_panel, 'Stamina Cost', True)
        self.u_58 = self.add_hex_entry(unknown_panel, 'U_58', max=MAX_UINT32)
        self.ki_required = self.add_num_entry(misc_panel, 'Ki Required', True)
        self.health_required = self.add_float_entry(misc_panel, 'Health Required')
        self.trans_stage = self.add_num_entry(misc_panel, 'Transformation\nStage')
        self.cus_aura = self.add_num_entry(misc_panel, 'CUS_AURA')
        self.u_68  = self.add_multiple_selection_entry(unknown_panel, 'Unknown Flags',  majorDimension=4,  choices=[
            ('', {
                'None': 0x0,
                'Use Skill Upgrades': 0x1,
                'Unknown (0x2)': 0x2,
                'Unknown (0x3)': 0x3,
                'Unknown (0x4)': 0x4,
                'Unknown (0x5)': 0x5,
                'Opponent Reached Ground?': 0x6,
                'Unknown (0x7)': 0x7,
                'Unknown (0x8)': 0x8,
                'Unknown (0x9)': 0x9,
                'Unknown (0xa)': 0xa,
                'Unknown (0xb)': 0xb,
                'Unknown (0xc)': 0xc,
                'Unknown (0xd)': 0xd,
                'Unknown (0xe)': 0xe,
                'Unknown (0xf)': 0xf,
            }, False)
        ])

        self.u_6a = self.add_hex_entry(unknown_panel, 'U_6A', max=MAX_UINT16)
        self.u_6c = self.add_multiple_selection_entry(
            misc_panel, 'Race/Gender', majorDimension=2, choices=[
                ('', {
                    'All Characters/Default': 0x0,
                    'Roster Characters only': 0x1,
                    'Male Humans only': 0x2,
                    'Female Humans only': 0x3,
                    'Male Saiyans only': 0x4,
                    'Female Saiyans only': 0x5,
                    'Namekians only': 0x6,
                    'Freeza Racists only': 0x7,
                    'Male Majins only': 0x8,
                    'Female Majins only': 0x9
                }, False)
            ])

        # Binds
        self.Bind(wx.EVT_TEXT, self.on_edit)
        self.Bind(wx.EVT_CHECKBOX, self.save_entry)
        self.Bind(wx.EVT_RADIOBOX, self.save_entry)
        EVT_RESULT(self, self.save_entry)

        # Publisher
        pub.subscribe(self.load_entry, 'load_entry')
        pub.subscribe(self.on_disable, 'disable')
        pub.subscribe(self.on_enable, 'enable')
        pub.subscribe(self.focus, 'focus')

        # Layout sizers
        self.Disable()
        self.SetSizer(sizer)
        self.SetAutoLayout(1)

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def on_disable(self):
        self.Disable()

    def on_enable(self):
        self.Enable()

    @add_entry
    def add_hex_entry(self, parent, _, *args, **kwargs):
        if 'size' not in kwargs:
            kwargs['size'] = (convert_to_px(150), -1)
        return HexCtrl(parent, *args, **kwargs)

    @add_entry
    def add_num_entry(self, panel, _, unsigned=False, *args, **kwargs):
        if 'size' not in kwargs:
            kwargs['size'] = (convert_to_px(150), -1)
        if unsigned:
            kwargs['min'], kwargs['max'] = kwargs.get('min', 0), kwargs.get('max', 65535)
        else:
            kwargs['min'], kwargs['max'] = kwargs.get('min', -32768), kwargs.get('max', 32767)
        return wx.SpinCtrl(panel, *args, **kwargs)

    @add_entry
    def add_single_selection_entry(self, panel, _, *args, **kwargs):
        return SingleSelectionBox(panel, *args, **kwargs)

    @add_entry
    def add_multiple_selection_entry(self, panel, _, *args, **kwargs):
        return MultipleSelectionBox(panel, *args, **kwargs)

    @add_entry
    def add_float_entry(self, panel, _, *args, **kwargs):
        if 'size' not in kwargs:
            kwargs['size'] = (convert_to_px(150), -1)
        if 'min' not in kwargs:
            kwargs['min'] = -3.402823466e38
        if 'max' not in kwargs:
            kwargs['max'] = 3.402823466e38

        kwargs['inc'] = 0.01
        return wx.SpinCtrlDouble(panel, *args, **kwargs)

    def on_edit(self, _):
        if not self.edit_thread:
            self.edit_thread = EditThread(self)
        else:
            self.edit_thread.new_sig()

    def load_entry(self, entry):
        for name in entry.__fields__:
            if name == 'child' or name == 'sibling':
                self[name].SetValue(address_to_index(entry[name]))
            else:
                self[name].SetValue(entry[name])
            
        if entry.address == 0:
            self.Disable()
        else:
            self.Enable()
        self.entry = entry

    def save_entry(self, _):
        self.edit_thread = None
        if not self.entry:
            return
        relabel = False
        for name in self.entry.__fields__:
            # SpinCtrlDoubles suck
            control = self[name]
            old_value = self.entry[name]
            if isinstance(control, wx.SpinCtrlDouble):
                try:
                    new_value = float(control.Children[0].GetValue())
                except ValueError:
                    # Keep old value if its mistyped
                    new_value = old_value
            elif name == "child" or name == "sibling":
                num_entries = len(self.parent_panel.bcm.entries)
                new_value = control.GetValue()
                if new_value >= num_entries:
                    new_value = num_entries - 1
                    control.SetValue(new_value)
                new_value = index_to_address(new_value)
            else:
                new_value = control.GetValue()
            if old_value != new_value:
                self.entry[name] = new_value
                if name == "child" or name == "sibling":
                    relabel = True

        if relabel:
            pub.sendMessage('relabel', index=address_to_index(self.entry.address))

    def focus(self, entry):
        page = self.notebook.FindPage(self[entry].GetParent())
        self.notebook.ChangeSelection(page)
        self[entry].SetFocus()


