import floppyforms as forms


class RadioSelectOptions(forms.RadioSelect):
    template_name = 'floppyforms/radio.html'

    def __init__(self, *args, **kwargs):
        required = kwargs.pop('required', False)
        stacked = kwargs.pop('stacked', False)

        self.is_required = required
        self.is_stacked = stacked

        super(RadioSelectOptions, self).__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        ctx = super(RadioSelectOptions, self).get_context(name, value, attrs)

        ctx["stacked"] = self.is_stacked
        ctx["required"] = self.is_required
        return ctx


class RadioSelectOpen(forms.RadioSelect):
    template_name = 'floppyforms/radioopen.html'

    def __init__(self, *args, **kwargs):
        required = kwargs.pop('required', False)
        stacked = kwargs.pop('stacked', False)

        self.is_required = required
        self.is_stacked = stacked

        super(RadioSelectOpen, self).__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        ctx = super(RadioSelectOpen, self).get_context(name, value, attrs)
        ctx["other"] = "Other"
        ctx["stacked"] = self.is_stacked
        ctx["required"] = self.is_required
        return ctx

    def value_from_datadict(self, data, files, name):
        x = data.get(name, None)

        if x == "other":
            y = data.get("%s_other" % name, None)
            return y
        return x


class ChooseOneForSubject(forms.RadioSelect):
    template_name = 'floppyforms/choose-one-for-subject.html'

    def __init__(self, subject, *args, **kwargs):
        self.subject = subject

        required = kwargs.pop('required', False)
        stacked = kwargs.pop('stacked', False)

        self.is_required = required
        self.is_stacked = stacked

        super(ChooseOneForSubject, self).__init__(*args, **kwargs)


    def get_context(self, name, value, attrs):
        ctx = super(ChooseOneForSubject, self).get_context(name, value, attrs)
        ctx["stacked"] = self.is_stacked
        ctx["required"] = True # is_required is getting overwritten somewhere.
        ctx["subject"] = self.subject
        return ctx


class ChooseOneForEach(forms.MultiWidget):
    def __init__(self, *args, **kwargs):
        self.num_widgets = len(kwargs["widgets"])
        super(ChooseOneForEach, self).__init__(*args, **kwargs)

    def decompress(self, value):
        if value:
            return value.split("|")

        return [None for x in range(1,self.num_widgets)]
